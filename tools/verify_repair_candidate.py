"""Independent original-CSV and graded-output comparisons; no product imports."""
import argparse
import csv
import hashlib
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs',type=Path,required=True)
    parser.add_argument('--reports',type=Path,required=True)
    parser.add_argument('--baseline',type=Path,required=True)
    args=parser.parse_args()
    current=json.loads(args.reports.read_text());baseline=json.loads(args.baseline.read_text())
    sources={};results=[]
    initial_questions={'APP-2026-010':'ENT-1001','APP-2026-018':'ENT-1801',
                       'APP-2026-020':'ENT-2000','APP-2026-021':'ENT-2100',
                       'APP-2026-022':'ENT-2201','APP-2026-032':'ENT-3201'}
    for batch in (1,2,3):
        folder=args.inputs/f'batch-{batch:02}'
        for name in ('verification-replies.csv','declared-history.csv','privilege-requests.csv'):
            with (folder/name).open(newline='') as stream:
                for line,row in enumerate(csv.DictReader(stream),2):
                    sources.setdefault(name,[]).append({'batch':batch,'csv_row':line,'row':row})
        raw=Path(current[str(batch)]).read_bytes();report=json.loads(raw)
        old=json.loads(Path(baseline[str(batch)]).read_text())
        assert len(report['applications'])==len(old['applications'])==40
        comparisons=[]
        for case,prior in zip(report['applications'],old['applications']):
            assert case['application_id']==prior['application_id']
            for field in ('revision','status','approval_decision_id','activation','monitored_conditions'):
                assert case[field]==prior[field],(batch,case['application_id'],field)
            assert case['packet']['presentable']==prior['packet']['presentable']
            assert [d['result'] for d in case['decisions']]==[d['result'] for d in prior['decisions']]
            assert all(e['state'] is not None for e in case['elements'].values())
            app=case['application_id']
            if app in initial_questions:
                entry=initial_questions[app]
                original=[r for r in sources['verification-replies.csv'] if r['row']['application_id']==app and r['row']['entry_id']==entry]
                declared=[r for r in sources['declared-history.csv'] if r['row']['application_id']==app and r['row']['entry_id']==entry and int(r['row']['revision'])==case['revision']]
                assert declared
                if batch==1:
                    # The only returned rows are the two inadmissible sources
                    # explicitly excluded by ATT's closed education list.
                    assert not original or all(r['row']['received_from'].startswith(('Applicant —','State medical society —')) for r in original)
                assert case['elements']['certification']['detail']['eligibility_question_pending']
                assert any(q['owner']=='Clinical Director' and 'eligibility' in q['item'] for q in case['action_queue'])
                assert not case['elements']['certification']['detail']['supported']
                comparisons.append({'application_id':app,'missing_or_inadmissible_initial_entry':entry,
                    'declared_source_rows':declared,'received_source_rows':original,
                    'rule':'PRIV application rule 6; ATT Professional education and post-graduate training row',
                    'conclusion':'Initial missing admissible degree/training evidence raises human question. No verified support yet closes it; later source receipt alone cannot establish missing accreditation.'})
        checks={c['application_id']:c for c in report['applications']}
        for app,entry in [('APP-2026-020','ENT-2000'),('APP-2026-022','ENT-2201')]:
            requests=[r for r in checks[app]['requests'] if r['subject_ref']==entry]
            assert requests
            assert requests[0]['request_satisfied']==(app=='APP-2026-020' and batch==3)
        results.append({'batch':batch,'report':current[str(batch)],'sha256':hashlib.sha256(raw).hexdigest(),
            'all_40_status_packet_boolean_decision_and_activation_comparisons_unchanged':True,
            'source_backed_questions':comparisons,'APP020_request_satisfied':batch==3,'APP022_request_satisfied':False,
            'summary':report['summary']})
    print(json.dumps({'method':__doc__,'limits':'No positive signature/CV/accreditation conclusion is inferred. The independent gap/referee/calendar checker is a separate required check. Synthetic regressions are separate evidence.','results':results},indent=2))


if __name__=='__main__':main()
