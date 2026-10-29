"""Independent audit facts/proposals; no credentialing imports or state writes."""
import collections,csv,hashlib,io,json,re,subprocess
from datetime import date,timedelta
from pathlib import Path
import jsonschema

ROOT=Path.cwd();OUT=ROOT/'.local/resubmission-audit-20261022'
readings=json.loads((ROOT/'docs/audit/source-readings.json').read_text())['readings']
def rows(name):
 out=[]
 for f in readings:
  if f.get('path','').endswith('/'+name):
   for n,r in enumerate(csv.DictReader(io.StringIO(f['content'])),2):out.append({'row':r,'batch':f['batch'],'path':f['path'],'csv_row':n,'url':f['url']})
 return out
def meta(text):return {k:v.strip() for k,v in re.findall(r'^\*\*([^*\n]+):\*\*[ \t]*([^\n]*)',text,re.M)}
decisions=[{'source':f['path'],'batch':f['batch'],'url':f['url'],'fields':meta(f['content'])} for f in readings if '/decisions/' in f.get('path','')]
versions=collections.Counter(d['fields'].get('Criteria version','<absent>') for d in decisions)
groups=collections.defaultdict(list)
for r in rows('verification-replies.csv'):groups[(r['row']['application_id'],r['row']['entry_id'])].append(r)
multi=[{'application_id':key[0],'entry_id':key[1],'observations':[{'source':r['path'],'csv_row':r['csv_row'],**{k:r['row'][k] for k in ['reply_id','received_date','verified_from','verified_to','outcome','received_from']}} for r in vals]} for key,vals in groups.items() if len(vals)>1]
schema=json.loads((ROOT/'snapshot.schema.json').read_text())
fragment={'$ref':'#/$defs/application','$defs':schema['$defs']}
index=json.loads((ROOT/'deliverables/workflow/current.json').read_text())
selected=['014','015','017','018','019','020','021','022','025','027','028','029','030','031','034','036','038']
cases=[];proposals=[]
for b,path in index.items():
 report=json.loads((ROOT/path).read_text());valid=[]
 for c in report['applications']:
  if c['application_id'][-3:] in selected:
   cases.append({'batch':int(b),'application_id':c['application_id'],'revision':c['revision'],'status':c['status'],'packet':c['packet']['presentable'],'elements':{k:v['state'] for k,v in c['elements'].items()},'referee_count':c['elements']['references']['detail']['qualifying_distinct_referees'],'decisions':[{'id':d['fields']['Decision ID'],'body':d['fields']['Body'],'revision':d['fields']['Revision'],'date':d['fields']['Decision date'],'result':d['result']} for d in c['decisions']],'CD_actions':[q['item'] for q in c['action_queue'] if q['owner']=='Clinical Director']})
  # Deliberately a proposal, not product output. Only replace unknown ELEMENT
  # states with their published 'something is still owed' representation.
  candidate={'application_id':c['application_id'],'revision':c['revision'],'status':c['status'],'elements':{k:v['state'] or 'outstanding' for k,v in c['elements'].items()},'packet_presentable':c['packet']['presentable'],'decisions':[{'decision_id':d['fields']['Decision ID'],'admitted':d['result']['admitted'],'reason':d['result']['reason'] if d['result']['admitted'] is False else None} for d in c['decisions']],'approval_decision_id':c['approval_decision_id'],'activation':c['activation'],'monitored_conditions':[{'condition':v['condition'],'due':v['due']} for v in c['monitored_conditions'] if not v['satisfied']],'action_queue':[{k:q[k] for k in ['item','owner','due']} for q in c['action_queue']]}
  errors=list(jsonschema.Draft202012Validator(fragment).iter_errors(candidate))
  if not errors:
   valid.append(c['application_id'])
   if b=='1' and c['application_id'].endswith('014'):
    (OUT/'proposed-APP014-batch1.json').write_text(json.dumps({'classification':'PROPOSAL ONLY — individual application, NOT an assessed snapshot or approved business result','basis':'Only final element None mapped to outstanding; existing known status and known false packet retained; G1/G2 tasks retained','application':candidate},indent=2)+'\n')
 proposals.append({'batch':int(b),'existing_schema_applications':report['summary']['schema_applications'],'proposed_individual_application_count':len(valid),'proposed_ids':valid,'full_snapshot_possible':False})
result={'method':'Standard-library parsing of original archived CSV/document text, calendar arithmetic, independent JSON Schema validation of explicitly labeled copies. No credentialing imports. No original output or source is modified.','decision_count':len(decisions),'criteria_versions_in_actual_decisions':dict(versions),'criteria_versions_requested':dict(collections.Counter(r['row']['criteria_version_cited'] for r in rows('privilege-requests.csv'))),'multiple_reply_entries':multi,'key_decision_sources':[d for d in decisions if d['fields'].get('Decision ID') in ['MEC-2026-024','GBD-2026-024','GBD-2026-034','MEC-2026-036']],'source_calculations':{'APP019_deadline':(date(2026,2,18)+timedelta(days=30)).isoformat(),'APP017_gap_days':(date(2019,11,5)-date(2019,4,1)).days+1,'APP018_gap_days':(date(2024,6,1)-date(2024,5,2)).days+1},'representation_proposals':proposals,'selected_actual_case_comparisons':cases}
(OUT/'additional-independent-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['selected_actual_case_comparisons','multiple_reply_entries','key_decision_sources']},indent=2))
print('Multiple-reply entry IDs:',[(m['application_id'],m['entry_id']) for m in multi])
print('Decision IDs actually used:',[(d['fields'].get('Decision ID'),d['fields'].get('Application')) for d in result['key_decision_sources']])
