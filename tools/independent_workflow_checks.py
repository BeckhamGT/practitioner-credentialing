"""Independent checks against original exports: no credentialing imports."""

import argparse
import csv
import hashlib
import json
from datetime import date,timedelta
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--inputs',type=Path,required=True);parser.add_argument('--reports',type=Path,required=True);args=parser.parse_args()
    index=json.loads((args.reports/'current.json').read_text());all_rows={};results=[]
    for batch in (1,2,3):
        folder=args.inputs/f'batch-{batch:02}';manifest=json.loads((folder/'input.manifest.json').read_text());clock=manifest['as_of']
        for name in ('applications.csv','peer-referees.csv','peer-reference-replies.csv','declared-history.csv','verification-replies.csv'):
            with (folder/name).open(newline='') as stream:all_rows.setdefault(name,[]).extend(csv.DictReader(stream))
        report_path=Path(index[str(batch)]);report=json.loads(report_path.read_text());assert report['as_of']==clock
        apps={}
        for row in all_rows['applications.csv']:
            if row['application_id'] not in apps or int(row['revision'])>int(apps[row['application_id']]['revision']):apps[row['application_id']]=row
        checks=[]
        for case in report['applications']:
            app=apps[case['application_id']];assert int(app['revision'])==case['revision']
            named={r['referee_id'] for r in all_rows['peer-referees.csv'] if r['application_id']==app['application_id'] and int(r['revision'])<=int(app['revision'])}
            assert case['intake']['conditions']['7_two_named_referees']==(len(named)>=2)
            latest={}
            for r in all_rows['peer-reference-replies.csv']:
                if r['application_id']==app['application_id'] and (r['referee_id'] not in latest or r['received_date']>latest[r['referee_id']]['received_date']):latest[r['referee_id']]=r
            count=0
            for r in latest.values():
                signed=date.fromisoformat(r['signature_date']);last=date.fromisoformat(r['last_worked_together_end']) if r['last_worked_together_end'] else signed
                # These source dates have no leap-day ambiguity; fail rather than clamp one.
                recent=signed.replace(year=signed.year-2)<=last<=signed
                current=signed<=date.fromisoformat(clock)<=signed.replace(year=signed.year+2)
                direct="We worked in the same department and I supervised several of the applicant's cases."==r['relationship_stated']
                count+=bool(r['related_or_partner']=='No' and r['referee_specialty_stated']==app['discipline'] and recent and current and direct and app['first_received_date']<=r['received_date']<=clock)
            assert count==case['elements']['references']['detail']['qualifying_distinct_referees'],app['application_id']
            history=[r for r in all_rows['declared-history.csv'] if (r['application_id'],r['revision'])==(app['application_id'],app['revision'])]
            school={r['to_date'] for r in history if r['entry_type']=='medical-school'};assert len(school)==1
            start=date.fromisoformat(next(iter(school))).toordinal()+1;end=date.fromisoformat(clock).toordinal();uncovered=set(range(start,end+1))
            for r in history:
                lower=date.fromisoformat(r['from_date']).toordinal();upper=date.fromisoformat(r['to_date'] or clock).toordinal();uncovered.difference_update(range(max(start,lower),min(end,upper)+1))
            segments=[]
            for n in sorted(uncovered):
                if not segments or n!=segments[-1][-1]+1:segments.append([])
                segments[-1].append(n)
            gaps=[{'from':date.fromordinal(s[0]).isoformat(),'to':date.fromordinal(s[-1]).isoformat(),'days':len(s)} for s in segments if len(s)>=30]
            assert gaps==[{k:g[k] for k in ('from','to','days')} for g in case['elements']['gaps']['detail']['gaps']]
            checks.append({'application_id':app['application_id'],'revision':case['revision'],'named_referees':len(named),'qualifying_current_returned_fields':count,'declared_gaps':gaps})
        notice=folder/'letters/2026-02-18_missing-items_APP-2026-019.md'
        if batch==1:
            assert notice.exists() and '2026-03-20' in notice.read_text();due=(date(2026,2,18)+timedelta(days=30)).isoformat();assert due=='2026-03-20'
        case19=next(c for c in report['applications'] if c['application_id']=='APP-2026-019');assert case19['status']==('intake-incomplete' if batch==1 else 'ineligible-clock-expired')
        results.append({'batch':batch,'report':str(report_path),'report_sha256':hashlib.sha256(report_path.read_bytes()).hexdigest(),'checks':checks,'actual_missing_item_due':'2026-03-20','status_APP019':case19['status']})
    print(json.dumps({'method':'Original CSVs and actual letter; daily set subtraction, distinct incremental referee IDs and calendar arithmetic; no product imports','results':results,'limits':'Checks these quantities and clocks, not complete intake, accreditation, CV reconciliation or clinical authority'},indent=2))


if __name__=='__main__':main()
