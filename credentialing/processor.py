"""Integrate immutable workflow reports with the guarded schema writer."""

from pathlib import Path

from .storage import Store
from .validation import GroundworkError, digest, json_bytes, read_json, schema_validate
from .workflow import process
from .workflow_store import WorkflowStore
from .writer import SnapshotWriter, snapshot_path


def process_run(evidence_store, state, work_store, previous, rules, rules_sha, root, schema_path):
    if root.is_symlink():raise GroundworkError("unsafe_path", "Output root cannot be a symlink")
    root = root.resolve(strict=True)
    evidence = Store(evidence_store)
    if work_store.resolve().is_relative_to(evidence.root) or evidence.root.is_relative_to(work_store.resolve()):
        raise GroundworkError("unsafe_path", "Workflow store must be separate from retained evidence store")
    retained = evidence.at(state);batch = retained["state"]["manifest"]["batch"]
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
    output = SnapshotWriter(root,schema).publish([candidate],{batch:report["as_of"]},[],external_outputs=[name])
    receipt.update(assessment_result="schema-snapshot-generated-or-unchanged",snapshot=output,
                   assessed_snapshot_written=output["result"]=="written", existing_snapshot_retained=output["result"]=="unchanged",
                   business_outcomes="Only source-supported or explicitly labeled synthetic facts; Git sealing separate")
    return receipt,0
