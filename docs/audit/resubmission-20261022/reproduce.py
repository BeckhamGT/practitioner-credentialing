from pathlib import Path
import subprocess,json,hashlib,datetime,shutil
repo=Path.cwd();out=repo/'.local/resubmission-audit-20261022';root=out/'actual'
root.mkdir();(root/'deliverables').mkdir();shutil.copyfile('deliverables/rules.md',root/'deliverables/rules.md')
py=str(repo/'.venv/bin/python'); logs=[]
def run(args,label,expected=0):
 p=subprocess.run([py,*map(str,args)],capture_output=True,cwd=repo)
 (out/(label+'.stdout')).write_bytes(p.stdout);(out/(label+'.stderr')).write_bytes(p.stderr)
 logs.append({'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':[py,*map(str,args)],'exit_code':p.returncode,'label':label})
 (out/'execution-log.json').write_text(json.dumps(logs,indent=2)+'\n')
 assert p.returncode==expected,(label,p.returncode,p.stderr.decode())
 return json.loads(p.stdout)
prev=None;work=None;results=[];index={};rule=hashlib.sha256(Path('references/element-rules.json').read_bytes()).hexdigest()
for b in range(1,4):
 inp=out/f'inputs/batch-{b:02}'
 run(['tools/prepare_batch.py','--archive','docs/audit/source-readings.json','--manifest',f'deliverables/evidence/input-manifests/batch-{b:02}.json','--output',inp],f'prepare-{b}')
 args=['-m','credentialing','stage','--input',inp,'--batch',b,'--store',out/'evidence']
 if prev:args+=['--previous-state',prev]
 s=run(args,f'stage-{b}');prev=s['state_sha256']
 args=['-m','credentialing','process','--store',out/'evidence','--state',prev,'--work-store',out/'workflow','--rules','references/element-rules.json','--rules-sha256',rule,'--root',root]
 if work:args+=['--previous-workflow',work]
 r=run(args,f'process-{b}',3);work=r['workflow_sha256']
 original=json.load(open('deliverables/workflow/current.json'))[str(b)]
 assert Path(original).read_bytes()==(root/r['report']).read_bytes()
 index[str(b)]=str(root/r['report']);results.append({'batch':b,'state_sha256':prev,'workflow_sha256':work,'summary':r['summary'],'matches_published_report_bytes':True,'assessment_result':r['assessment_result']})
r=run(args,'rerun-3',3);assert r['workflow_result']=='unchanged'
(root/'deliverables/workflow/current.json').write_text(json.dumps(index,indent=2)+'\n')
run(['tools/independent_workflow_checks.py','--inputs',out/'inputs','--reports',root/'deliverables/workflow'],'independent-checks')
for b in range(1,4):run(['-m','credentialing','verify-snapshot','--root','deliverables/synthetic/workflow-demo','--path',f'deliverables/snapshots/batch-{b:02}.json','--schema','snapshot.schema.json'],f'verify-retained-synthetic-{b}')
run(['-m','tools.workflow_demo','--output',out/'synthetic/fresh-demo'],'fresh-synthetic')
(out/'baseline-results.json').write_text(json.dumps({'baseline_commit':subprocess.check_output(['git','rev-parse','HEAD']).decode().strip(),'batches':results,'actual_snapshot_paths_exist':[Path(f'deliverables/snapshots/batch-{b:02}.json').exists() for b in range(1,4)],'rerun_unchanged':True,'synthetic_existing_validated':True,'synthetic_fresh_demonstrated':True},indent=2)+'\n')
print(json.dumps(results,indent=2))
