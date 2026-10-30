"""Integrate immutable workflow reports with the guarded schema writer."""

from pathlib import Path
import os
import uuid
from datetime import datetime, timezone

from .storage import Store
from .validation import GroundworkError, digest, json_bytes, read_json, schema_validate
from .workflow import process
from .workflow_store import WorkflowStore
from .writer import SnapshotWriter, snapshot_path


def _process_run(evidence_store, state, work_store, previous, rules, rules_sha, root, schema_path, audit_outputs=(), attempt_context=None):
    if root.is_symlink():raise GroundworkError("unsafe_path", "Output root cannot be a symlink")
    root = root.resolve(strict=True)
    evidence = Store(evidence_store)
    if work_store.resolve().is_relative_to(evidence.root) or evidence.root.is_relative_to(work_store.resolve()):
        raise GroundworkError("unsafe_path", "Workflow store must be separate from retained evidence store")
    retained = evidence.at(state);batch = retained["state"]["manifest"]["batch"]
    if attempt_context is not None:
        attempt_context.update(batch=batch,as_of=retained["state"]["manifest"]["as_of"],consumed_manifest=retained["state"]["manifest"])
    workflow = WorkflowStore(work_store);prior = workflow.predecessor(batch,state,previous)
    report = process(evidence,state,rules,rules_sha,prior,previous)
    schema = read_json(schema_path.read_bytes())
    for app in report["applications"]:
        if app["schema_application"] is not None:
            schema_validate(app["schema_application"],{"$schema":schema["$schema"],"$defs":schema["$defs"],"$ref":"#/$defs/application"})
    run_sha,change = workflow.commit(report)
    folder = root/"deliverables/workflow"
    if any(p.is_symlink() for p in [folder,*folder.parents]):raise GroundworkError("unsafe_path", "Symlinked report output")
    folder.mkdir(parents=True,exist_ok=True);name=f"deliverables/workflow/batch-{batch:02}-{run_sha}.json";path = root/name
    raw = json_bytes(report)
    if path.exists():
        if path.is_symlink() or path.read_bytes()!=raw:raise GroundworkError("changed_report", "Preserve existing report, do not overwrite differing bytes")
    else:
        with path.open("xb") as out:out.write(raw)
    if attempt_context is not None:
        attempt_context.update(retained_workflow_sha256=run_sha,written_report=name)
    receipt = {"operation":"process", "workflow_result":change, "workflow_sha256":run_sha,
               "previous_workflow_sha256":previous, "batch":batch,"as_of":report["as_of"],"report":name,
               "summary":report["summary"],"assessed_snapshot_written":False,
               "schema_projection_conflicts":report["schema_projection_conflicts"]}
    if report["schema_projection_conflicts"]:
        receipt["assessment_result"] = "blocked-at-schema-projection"
        return receipt,3
    if batch>1 and not (root/snapshot_path(batch-1)).exists():
        receipt["assessment_result"] = "blocked-missing-assessed-predecessor"
        return receipt,3
    prefix = "SYNTH-workflow" if report["dataset"]=="synthetic-demonstration" else "workflow"
    candidate = {"schema_version":"credentialing-snapshot/1","snapshot_id":f"{prefix}-{batch:02}-{run_sha[:24]}",
                 "predecessor":None,"batch":batch,"as_of":report["as_of"],
                 "consumed":{"record_files":[f["path"] for f in report["source_manifest"]["files"] if f["kind"]=="records"],
                             "documents":[f["path"] for f in report["source_manifest"]["files"] if f["kind"] in ("document","batch-readme")]},
                 "produced":[snapshot_path(batch)],"rules_file":"deliverables/rules.md",
                 "applications":[a["schema_application"] for a in report["applications"]]}
    output = SnapshotWriter(root,schema).publish([candidate],{batch:report["as_of"]},[],external_outputs=[name, *audit_outputs])
    receipt.update(assessment_result="schema-snapshot-generated-or-unchanged",snapshot=output,
                   assessed_snapshot_written=output["result"]=="written", existing_snapshot_retained=output["result"]=="unchanged",
                   business_outcomes="Only source-supported or explicitly labeled synthetic facts; Git sealing separate")
    return receipt,0


def _atomic_json(path, value):
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with temporary.open("xb") as stream:
            stream.write(json_bytes(value));stream.flush();os.fsync(stream.fileno())
        os.replace(temporary,path)
    finally:
        temporary.unlink(missing_ok=True)


def process_run(evidence_store, state, work_store, previous, rules, rules_sha, root, schema_path):
    """Persist the latest attempt separately from the last consumed workflow.

    An unavailable output filesystem cannot guarantee a disk receipt: the CLI
    still reports that failure to stderr. No older result is called that attempt.
    """
    if any(p.is_symlink() for p in (root,*root.parents)):
        raise GroundworkError("unsafe_path", "Output root cannot be symlinked")
    root = root.resolve(strict=True)
    folder = root/"deliverables/workflow"
    if any(p.is_symlink() for p in (folder,*folder.parents)):
        raise GroundworkError("unsafe_path", "Receipt output cannot be symlinked")
    folder.mkdir(parents=True,exist_ok=True)
    receipts=folder/"attempts"
    if receipts.is_symlink():raise GroundworkError("unsafe_path", "Receipt directory cannot be symlinked")
    receipts.mkdir(exist_ok=True)
    for path in (folder/"latest-attempt.json",folder/"current.json",root/"deliverables/run-log.md"):
        if path.is_symlink():raise GroundworkError("unsafe_path", "Receipt pointer/log cannot be symlinked")
    identifier=uuid.uuid4().hex
    relative=f"deliverables/workflow/attempts/{identifier}.json"
    record={"attempt_id":identifier,"started_at_utc":datetime.now(timezone.utc).isoformat(),
            "operation":"process","state":state,"previous_workflow":previous,"batch":None,"as_of":None,
            "command":["python","-m","credentialing","process","--store",str(evidence_store),"--state",state,"--work-store",str(work_store),"--rules",str(rules),"--rules-sha256",rules_sha,"--root",str(root)]+(["--previous-workflow",previous] if previous else []),
            "arguments":{"store":str(evidence_store),"work_store":str(work_store),"rules":str(rules),"rules_sha256":rules_sha,"root":str(root)},
            "result":"running","receipt":relative}
    def save():
        _atomic_json(root/relative,record)
        _atomic_json(folder/"latest-attempt.json",record)
    save()
    if not (folder/"current.json").exists():
        _atomic_json(folder/"current.json",{})
    try:
        result,code=_process_run(evidence_store,state,work_store,previous,rules,rules_sha,root,schema_path,
            [relative,"deliverables/workflow/latest-attempt.json","deliverables/workflow/current.json"],record)
        record.update(result="consumed",exit_code=code,output=result)
        index_path=folder/"current.json"
        index=read_json(index_path.read_bytes()) if index_path.exists() else {}
        index[str(result["batch"])]=result["report"]
        _atomic_json(index_path,index)
        return result,code
    except (GroundworkError,OSError) as exc:
        record.update(result="failed",exit_code=2,error=getattr(exc,"code","filesystem_error"),message=str(exc),affected_scope={"requested_state":state})
        raise
    finally:
        record["ended_at_utc"]=datetime.now(timezone.utc).isoformat()
        save()
        # An interrupted snapshot transaction owns run-log.md until recovery.
        # Its immutable attempt receipt remains available immediately; flush any
        # unlinked receipts into the human log after recovery on the next run.
        if not (root/".local/snapshot-writer/active.json").exists():
            log_path=root/"deliverables/run-log.md"
            prior=log_path.read_text() if log_path.exists() else ""
            with log_path.open("a") as log:
                for path in sorted(receipts.glob("*.json")):
                    entry=read_json(path.read_bytes())
                    if entry["attempt_id"] not in prior:
                        log.write("\n- Process attempt `"+entry["attempt_id"]+"`: "+entry["result"]+"; exact arguments, UTC times, consumed state, produced outputs/error and scope: [receipt](workflow/attempts/"+path.name+").\n")
