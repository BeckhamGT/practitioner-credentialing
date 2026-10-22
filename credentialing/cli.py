"""Command interface restricted to the learner-authorized foundation."""

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
from .validation import GroundworkError, load_batch


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Evidence-only groundwork; business processing is blocked by G1/G2.")
    commands = parser.add_subparsers(dest="command", required=True)
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
    commands.add_parser("run", help="Reserved business operation: blocked until source clarification and learner review")
    args = parser.parse_args(argv)
    try:
        if args.command == "run":
            raise GroundworkError("business_blocked", "G1/G2 unresolved; completeness, packet readiness, assessed snapshots and business actions are disabled")
        if args.command == "timeline":
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
        return 3 if exc.code == "business_blocked" else 2
    except OSError:
        print(json.dumps({"result": "operation-failed", "error": "filesystem_error",
                          "message": "Filesystem operation failed; inspect input/store without overwriting evidence",
                          "assessed_snapshot_written": False}), file=sys.stderr)
        return 2
