"""Run the full CLI on three explicitly synthetic export batches."""

import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

from credentialing.snapshots import verify_snapshot
from credentialing.validation import digest,json_bytes
from tools.synthetic_workflow import APP,decision_document,initial,make_batch


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if 'synthetic' not in args.output.parts or args.output.exists():parser.error('Use a new explicitly synthetic directory; existing output is preserved')
    repo=Path(__file__).resolve().parents[1];root=args.output.resolve();root.mkdir(parents=True);(root/'deliverables').mkdir();(root/'deliverables/rules.md').write_bytes((repo/'deliverables/rules.md').read_bytes())
    rows,docs=initial();inputs=[make_batch(root/'inputs/batch-01',1,rows,docs),make_batch(root/'inputs/batch-02',2,documents={'decisions/SYNTH-GB.md':decision_document()}),make_batch(root/'inputs/batch-03',3,documents={'letters/SYNTH-satisfaction.md':f'# SYNTHETIC invented satisfaction\n\n**Date:** 2026-05-02\n**Application:** {APP}\n**Recorded by:** Ms. Renata Kowalczyk, CPMSM\n**Condition satisfied:** SYNTH named monitoring evidence\n'})]
    logs=[];prior_state=None;prior_run=None;receipts=[];last_command=None
    def execute(command):
        stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();p=subprocess.run(command,cwd=repo,capture_output=True)
        if p.returncode!=0:raise RuntimeError(p.stderr.decode()+p.stdout.decode())
        value=json.loads(p.stdout);logs.append({'started_at_utc':stamp,'command':command,'exit_code':p.returncode,'stdout_sha256':digest(p.stdout),'receipt':value});return value
    for batch,folder in enumerate(inputs,1):
        command=[sys.executable,'-m','credentialing','stage','--input',str(folder),'--batch',str(batch),'--store',str(root/'.local/evidence')]
        if prior_state:command+=['--previous-state',prior_state]
        stage=execute(command)
        command=[sys.executable,'-m','credentialing','process','--store',str(root/'.local/evidence'),'--state',stage['state_sha256'],'--work-store',str(root/'.local/workflow'),'--rules',str(repo/'references/element-rules.json'),'--rules-sha256',digest((repo/'references/element-rules.json').read_bytes()),'--root',str(root)]
        if prior_run:command+=['--previous-workflow',prior_run]
        receipt=execute(command);receipts.append(receipt);prior_state=stage['state_sha256'];prior_run=receipt['workflow_sha256'];last_command=command
    raw=(root/'deliverables/snapshots/batch-03.json').read_bytes();repeat=execute(last_command);assert repeat['workflow_result']=='unchanged' and raw==(root/'deliverables/snapshots/batch-03.json').read_bytes()
    reports=[json.loads((root/r['report']).read_bytes()) for r in receipts];cases=[r['applications'][0] for r in reports]
    assert [a['status'] for a in cases]==['packet-presentable','approved-not-yet-effective','active-with-conditions']
    assert cases[-1]['activation']['privileges']==['PRIV-FM'] and cases[-1]['activation']['cycle_end']=='2027-04-24'
    proof={'dataset':'SYNTHETIC ONLY; every source, review fact and decision for SYNTH-WORKFLOW is invented',
           'engineering_assumptions':['Linked signed/dated application evidence','CV current at intake and reconciled','All held credentials declared','Degree and training accreditation established by synthetic MSP observations'],
           'real_office_rules':'Pinned original procedure/source/authority/privilege rules; no office-rule waiver',
           'statuses':[a['status'] for a in cases],'exact_grants':cases[-1]['activation'],
           'conditions':cases[-1]['monitored_conditions'],'chronology':[{'batch':r['batch'],'as_of':r['as_of'],'workflow_sha256':s['workflow_sha256'],'predecessor':r['previous_workflow_sha256']} for r,s in zip(reports,receipts)],
           'unchanged_rerun_byte_identical':True,'snapshot_verification':verify_snapshot(root,'deliverables/snapshots/batch-03.json',json.loads((repo/'snapshot.schema.json').read_text())),
           'limits':'Conditional demonstration, not verified outcomes for supplied applicants. Other exception/failure/recovery paths have separate synthetic tests.'}
    (root/'proof.json').write_bytes(json_bytes(proof));(root/'execution-log.json').write_bytes(json_bytes(logs));print(json.dumps({'proof':str(root/'proof.json'),'statuses':proof['statuses'],'dataset':proof['dataset']},indent=2))


if __name__=='__main__':main()
