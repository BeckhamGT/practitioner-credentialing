"""Deliberate SYNTHETIC writer lifecycle probe, never supplied-applicant results."""

import argparse
import copy
import json
from pathlib import Path
from unittest.mock import patch

from credentialing.snapshots import verify_snapshot
from credentialing.validation import GroundworkError, digest, json_bytes
from credentialing.writer import SnapshotWriter, snapshot_path


CLOCKS = {1: "2026-03-16", 2: "2026-04-20", 3: "2026-05-18"}


def candidate(batch, corrected=False):
    app = {"application_id": "SYNTH-ONLY", "revision": 1, "status": "in-verification",
           "elements": {k: "outstanding" for k in ("licensure", "experience", "gaps", "education", "certification", "references")},
           "packet_presentable": False, "decisions": [{"decision_id": "SYNTH-D", "admitted": False, "reason": "body-authority"}],
           "approval_decision_id": None, "activation": None, "monitored_conditions": [],
           "action_queue": [{"item": "SYNTHETIC corrected source request" if corrected and batch == 1 else "SYNTHETIC outstanding evidence", "owner": "Medical Services Professional", "due": None}]}
    return {"schema_version": "credentialing-snapshot/1", "snapshot_id": f"SYNTH-{'NEW-' if corrected else ''}{batch}",
            "batch": batch, "as_of": CLOCKS[batch], "predecessor": None,
            "consumed": {"record_files": ["SYNTH.csv"], "documents": []}, "produced": [snapshot_path(batch)],
            "rules_file": "rules.md", "applications": [app]}


def setup(root):
    root.mkdir(parents=True)
    (root / "rules.md").write_text("SYNTHETIC ONLY. Assumed complete intake; all six elements outstanding. No actual applicant conclusion.\n")
    (root / "SYNTH.csv").write_text("application_id\nSYNTH-ONLY\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    args = parser.parse_args()
    if "synthetic" not in args.output.parts or args.output.exists():
        parser.error("Use a new, explicitly synthetic output root; existing output is preserved")
    root = args.output.resolve();setup(root)
    schema = json.loads(args.schema.read_bytes());writer = SnapshotWriter(root, schema)
    operations = []
    for batch in (1, 2, 3):
        operations.append(writer.publish([candidate(batch)], CLOCKS, []))
    before = {b: (root / snapshot_path(b)).read_bytes() for b in CLOCKS}
    unchanged = copy.deepcopy(candidate(3));unchanged["snapshot_id"] = "SYNTH-UNUSED-REQUEST-ID"
    operations.append(writer.publish([unchanged], CLOCKS, []))
    assert before[3] == (root / snapshot_path(3)).read_bytes()
    try:
        writer.publish([candidate(1, True)], CLOCKS, [], reason="SYNTHETIC source correction")
        raise AssertionError("Expected downstream regeneration rejection")
    except GroundworkError as exc:
        assert exc.code == "downstream_regeneration"
        operations.append({"expected_failure": exc.code, "prior_bytes_unchanged": all((root / snapshot_path(b)).read_bytes() == raw for b, raw in before.items())})
    operations.append(writer.publish([candidate(b, True) for b in CLOCKS], CLOCKS, [], reason="SYNTHETIC correction; regenerate all affected later occurrences"))
    registry = json.loads((root / "deliverables/snapshots/history/index.json").read_bytes())
    for raw in before.values():
        retained = next(x for x in registry["occurrences"] if x["sha256"] == digest(raw))
        assert (root / retained["retained_path"]).read_bytes() == raw
    chain = verify_snapshot(root, snapshot_path(3), schema)
    probe = root / "failure-probe";setup(probe);recovery = SnapshotWriter(probe, schema)
    recovery.publish([candidate(1)], CLOCKS, [])
    old = (probe / snapshot_path(1)).read_bytes();atomic = recovery._atomic
    def fail(path, raw):
        if path == probe / snapshot_path(2):
            raise OSError("SYNTHETIC injected write failure, not a production incident")
        return atomic(path, raw)
    with patch.object(recovery, "_atomic", side_effect=fail):
        try:
            recovery.publish([candidate(2)], CLOCKS, [])
            raise AssertionError("Expected interrupted writer")
        except GroundworkError as exc:
            assert exc.code == "writer_interrupted"
            operations.append({"expected_failure": exc.code, "scope": "isolated synthetic batch 2 working files"})
    try:
        verify_snapshot(probe, snapshot_path(1), schema)
        raise AssertionError("Interrupted working files cannot count as current success")
    except GroundworkError as exc:
        assert exc.code == "writer_recovery_required"
        operations.append({"verification_blocked": exc.code})
    operations.append(recovery.recover())
    assert old == (probe / snapshot_path(1)).read_bytes()
    assert not (probe / snapshot_path(2)).exists()
    operations.append(recovery.publish([candidate(2)], CLOCKS, []))
    proof = {"dataset": "SYNTHETIC ONLY; no supplied applicants", "assumptions": ["Complete synthetic intake", "Six elements outstanding", "A known body-authority refusal"],
             "operations": operations, "current_chain": chain, "old_occurrences_retained_byte_for_byte": True,
             "failure_recovery_preserved_prior_snapshot": True, "recovered_chain": verify_snapshot(probe, snapshot_path(2), schema),
             "limits": "Writer/serialization demonstration. Business facts are supplied fixtures. Git sealing occurs only at a later explicit local commit."}
    (root / "proof.json").write_bytes(json_bytes(proof))
    print(json.dumps(proof, indent=2))


if __name__ == "__main__":
    main()
