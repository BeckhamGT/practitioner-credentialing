"""Evidence loading, dated workflow processing and guarded snapshot generation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .storage import Store
from .review import review
from .timeline import timeline
from .snapshots import verify_snapshot
from .validation import read_json
from .elements import assess_elements
from .writer import SnapshotWriter
from .validation import GroundworkError, load_batch
from .processor import process_run


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Process credentialing evidence chronologically; retain scoped unknowns and human authority.")
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("process", help="Complete dated business evaluation, immutable continuation and truthful schema projection")
    command.add_argument("--store", type=Path, required=True, help="Retained evidence store")
    command.add_argument("--state", required=True)
    command.add_argument("--work-store",type=Path,required=True)
    command.add_argument("--previous-workflow")
    command.add_argument("--rules",type=Path,required=True)
    command.add_argument("--rules-sha256",required=True)
    command.add_argument("--root",type=Path,default=Path.cwd(),help="Existing output workspace with rules register")
    for name in ("check-input", "stage"):
        command = commands.add_parser(name)
        command.add_argument("--input", type=Path, required=True, help="One physical batch directory with input.manifest.json")
        command.add_argument("--batch", type=int, required=True)
        if name == "stage":
            command.add_argument("--store", type=Path, required=True)
            command.add_argument("--previous-state", help="Exact prior state SHA-256; required for continuation")
    command = commands.add_parser("inspect-state")
    command.add_argument("--store", type=Path, required=True)
    command = commands.add_parser("review", help="Read-only independent record checks; never a credentialing snapshot")
    command.add_argument("--store", type=Path, required=True)
    command.add_argument("--state", required=True, help="Exact evidence-state SHA; never infer from a newer HEAD")
    command.add_argument("--policy", type=Path, required=True)
    command.add_argument("--policy-sha256", required=True)
    command = commands.add_parser("timeline", help="Retained revision/request/decision evidence; not an assessed snapshot")
    command.add_argument("--store", type=Path, required=True)
    command.add_argument("--state", required=True)
    command.add_argument("--rules", type=Path, required=True)
    command.add_argument("--rules-sha256", required=True)
    command = commands.add_parser("verify-snapshot", help="Read-only schema and predecessor checks; not business acceptance")
    command.add_argument("--root", type=Path, required=True)
    command.add_argument("--path", required=True)
    command.add_argument("--schema", type=Path, required=True)
    command = commands.add_parser("recover-writer", help="Restore prior working outputs from a verified interrupted local writer journal")
    command.add_argument("--root", type=Path, required=True)
    command.add_argument("--schema", type=Path, required=True)
    command = commands.add_parser("elements", help="Independent element facts; no unsupported schema projection")
    command.add_argument("--store", type=Path, required=True)
    command.add_argument("--state", required=True)
    command.add_argument("--rules", type=Path, required=True)
    command.add_argument("--rules-sha256", required=True)
    command = commands.add_parser("run", help="Legacy independent-report boundary; use process for the full workflow")
    command.add_argument("--store", type=Path)
    command.add_argument("--state")
    command.add_argument("--rules", type=Path)
    command.add_argument("--rules-sha256")
    command.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "process":
            schema_path = Path(__file__).resolve().parents[1]/"snapshot.schema.json"
            result, code = process_run(args.store,args.state,args.work_store,args.previous_workflow,args.rules,args.rules_sha256,args.root,schema_path)
            print(json.dumps(result,sort_keys=True,indent=2))
            return code
        if args.command == "run":
            values = (args.store, args.state, args.rules, args.rules_sha256, args.report)
            if not any(values):
                raise GroundworkError("business_blocked", "G1/G2 unresolved; completeness, packet readiness, assessed snapshots and business actions are disabled")
            if not all(values):
                raise GroundworkError("run_arguments", "Supply store, pinned state/rules and a separate assessment-report path")
            if "snapshots" in args.report.parts or any(p.is_symlink() for p in [args.report, *args.report.parents]):
                raise GroundworkError("unsafe_path", "An internal assessment report cannot occupy a snapshot path")
            result = assess_elements(Store(args.store), args.state, args.rules, args.rules_sha256)
            # Match the stdout report exactly, including Unicode escaping.
            raw = (json.dumps(result, sort_keys=True, indent=2) + "\n").encode("utf-8")
            if args.report.exists():
                if args.report.read_bytes() != raw:
                    raise GroundworkError("changed_report", "Preserve existing report; choose a new occurrence path")
            else:
                args.report.parent.mkdir(parents=True, exist_ok=True)
                with args.report.open("xb") as stream:
                    stream.write(raw)
            blocked = list(result["representation_conflicts"])
            schema_path = Path(__file__).resolve().parents[1] / "snapshot.schema.json"
            writer = SnapshotWriter(Path.cwd(), read_json(schema_path.read_bytes()))
            writer.publish([], {result["batch"]: result["as_of"]}, blocked)
            raise GroundworkError("snapshot_unrepresentable", "No supported schema candidate; independent assessment report retained")
        if args.command == "recover-writer":
            result = SnapshotWriter(args.root, read_json(args.schema.read_bytes())).recover()
        elif args.command == "elements":
            result = assess_elements(Store(args.store), args.state, args.rules, args.rules_sha256)
        elif args.command == "timeline":
            result = timeline(Store(args.store), args.state, args.rules, args.rules_sha256)
        elif args.command == "verify-snapshot":
            result = verify_snapshot(args.root, args.path, read_json(args.schema.read_bytes()))
        elif args.command == "review":
            result = review(Store(args.store), args.state, args.policy, args.policy_sha256)
        elif args.command == "inspect-state":
            current = Store(args.store).current()
            if current is None:
                raise GroundworkError("missing_state", "No current evidence state; no state was reconstructed")
            result = {"operation": "inspect-state", "phase": "evidence-only", "business_blockers": ["G1", "G2"],
                      "state_sha256": current["sha256"], "summary": current["summary"],
                      "batches": [{"batch": s["manifest"]["batch"], "as_of": s["manifest"]["as_of"],
                                   "state_sha256": sha} for sha, s, _ in current["chain"]],
                      "assessed_snapshot_written": False}
        else:
            if args.command == "stage" and args.store.resolve().is_relative_to(args.input.resolve()):
                raise GroundworkError("unsafe_path", "State store must be outside the input directory")
            manifest, raw, contents, summary = load_batch(args.input, args.batch)
            if args.command == "check-input":
                result = {"operation": "check-input", "result": "structure-valid", "batch": manifest["batch"],
                          "as_of": manifest["as_of"], **summary, "business_blockers": ["G1", "G2"],
                          "assessed_snapshot_written": False}
            else:
                result = Store(args.store).stage(manifest, raw, contents, args.previous_state)
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except GroundworkError as exc:
        print(json.dumps({"result": "operation-failed", "error": exc.code, "message": str(exc),
                          "assessed_snapshot_written": False}, sort_keys=True), file=sys.stderr)
        return 3 if exc.code in ("business_blocked", "snapshot_unrepresentable") else 2
    except OSError:
        print(json.dumps({"result": "operation-failed", "error": "filesystem_error",
                          "message": "Filesystem operation failed; inspect input/store without overwriting evidence",
                          "assessed_snapshot_written": False}), file=sys.stderr)
        return 2
