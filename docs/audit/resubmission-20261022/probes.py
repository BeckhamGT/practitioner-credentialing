"""Audit-only SYNTH probes. No source, runtime, or sealed result is changed."""
import sys,json,copy
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tests.test_workflow import WorkflowTests
from tools.synthetic_workflow import initial,decision_document
results=[]
def session():
 t=WorkflowTests();t.setUp();return t
# New contradictory verification must reopen its entry; an old positive cannot erase it.
t=session()
try:
 s=t.start();r,_=t.run_batch(s);rows,_=initial();corrected=copy.deepcopy(rows['verification-replies.csv'][-1]);corrected.update(reply_id='SYNTH-CORRECTION',received_date='2026-04-01',verified_from='2003-08-01',outcome='confirmed-with-discrepancy',notes='SYNTH corrected earlier verification; original start date was wrong.')
 s2=t.stage(2,{'verification-replies.csv':[corrected]},previous=s);r2,code=t.run_batch(s2,r['workflow_sha256']);c=t.result(r2)['applications'][0]
 entry=c['elements']['experience']['detail']['entries'][0]
 results.append({'probe':'later_source_correction','dataset':'SYNTHETIC ONLY','expected':'affected entry unresolved discrepancy; preserve both replies; no guessed corrected declaration','observed_state':c['elements']['experience']['state'],'observed_packet':c['packet']['presentable'],'reply_discrepancy_flags':[v['discrepancy'] for v in entry['replies']],'replies_retained':len(entry['replies']),'confirmed_gap':c['elements']['experience']['state']=='resolved'})
finally:t.doCleanups()
# Applicant-carried material does not answer the request to the actual source.
t=session()
try:
 def change(rows,docs):
  rows['verification-replies.csv'][0]['received_from']='Applicant — copy of diploma'
  from tools.synthetic_workflow import record
  rows['verification-attempts.csv'].append(record('verification-attempts.csv',attempt_id='SYNTH-SOURCE-REQUEST',application_id='SYNTH-WORKFLOW',element='education-and-training',subject_ref='SYNTH-E0',attempted_with='Registrar — SYNTH School',attempt_date='2026-01-02',method='portal',outcome='request sent'))
 s=t.start(change);r,_=t.run_batch(s);c=t.result(r)['applications'][0]
 req=next(x for x in c['requests'] if x['subject_ref']=='SYNTH-E0')
 results.append({'probe':'inadmissible_reply_suppresses_required_source_followup','dataset':'SYNTHETIC ONLY','expected':'unanswered registrar request remains due for follow-up; diploma receipt is not a source reply','element_state':c['elements']['education']['state'],'request':{k:req[k] for k in ['recorded_attempt_count','reply_observed','reply_qualifies','request_satisfied','operationally_closed']},'source_followup_actions':[q for q in c['action_queue'] if 'SYNTH-E0' in q['item']]})
finally:t.doCleanups()
# A cited version absent from pinned sources must not silently use another version.
t=session()
try:
 s=t.start();r,_=t.run_batch(s);doc=decision_document(outcome='approved',**{'Criteria version':'SYNTH-UNAVAILABLE-VERSION'})
 s2=t.stage(2,docs={'decisions/SYNTH-version.md':doc},previous=s);r2,code=t.run_batch(s2,r['workflow_sha256']);c=t.result(r2)['applications'][0]
 results.append({'probe':'unknown_criteria_version','dataset':'SYNTHETIC ONLY','expected':'unsupported cited policy version surfaced, no silent evaluation under LARK-PRIV-2026.1','decision':c['decisions'][0]['result'],'approval':c['approval_decision_id'],'activation':c['activation'],'confirmed_gap':c['approval_decision_id'] is not None})
finally:t.doCleanups()
# A missing training reply has an express temporary eligibility-routing rule.
t=session()
try:
 def change(rows,docs):rows['verification-replies.csv']=[r for r in rows['verification-replies.csv'] if r['entry_id']!='SYNTH-E1']
 s=t.start(change);r,_=t.run_batch(s);c=t.result(r)['applications'][0]
 results.append({'probe':'no_yet_verified_training_support','dataset':'SYNTHETIC ONLY','expected':'PRIV rule 6 asks Clinical Director while nothing yet verified supports any group; no discontinuation invented','certification':c['elements']['certification'],'CD_actions':[q['item'] for q in c['action_queue'] if q['owner']=='Clinical Director']})
finally:t.doCleanups()
out=Path('.local/resubmission-audit-20261022/diagnostic-probes.json');out.write_text(json.dumps(results,indent=2)+'\n')
for r in results:
 print(json.dumps({k:v for k,v in r.items() if k!='certification'},indent=2))
print('No-support certification:',next(x for x in results if 'certification' in x)['certification']['state'])
