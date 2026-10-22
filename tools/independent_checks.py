"""Recompute raw-source quantities without importing the Skill implementation."""

import argparse
import csv
import hashlib
import json
import re
from datetime import date
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--reports", type=Path, required=True)
    parser.add_argument("--application", required=True)
    parser.add_argument("--subject", required=True)
    args = parser.parse_args()
    revisions, attempts, decisions = [], [], []
    checks = []
    for batch in (1, 2, 3):
        folder = args.inputs / f"batch-{batch:02}"
        def rows(name):
            with (folder / name).open(newline="", encoding="utf-8") as file:
                return list(csv.DictReader(file))
        revisions.extend(rows("applications.csv"))
        attempts.extend(rows("verification-attempts.csv"))
        for path in (folder / "decisions").glob("*.md"):
            match = re.search(r"^\*\*Decision ID:\*\*[ \t]*(.+)$", path.read_text(), re.MULTILINE)
            if not match:
                raise ValueError("Decision metadata absent")
            decisions.append(match.group(1).strip())
        candidates = list(args.reports.glob(f"batch-{batch:02}-timeline-*.json"))
        if len(candidates) != 1:
            raise ValueError("Select one report occurrence per batch in an isolated reports folder")
        raw = candidates[0].read_bytes();report = json.loads(raw)
        counts = {"applications": len({r["application_id"] for r in revisions}),
                  "revision_occurrences": len(revisions), "attempt_occurrences": len(attempts),
                  "decision_occurrences": len(decisions)}
        if any(report["summary"][key] != value for key, value in counts.items()):
            raise ValueError("Source counts disagree with report")
        if {d["decision_id"] for d in report["decision_register"]} != set(decisions):
            raise ValueError("Decision identity coverage differs")
        checks.append({"batch": batch, "counts": counts, "report_sha256": hashlib.sha256(raw).hexdigest()})
    chosen = sorted([a for a in attempts if a["application_id"] == args.application
                     and a["subject_ref"] == args.subject], key=lambda a: a["attempt_date"])
    days = [date.fromisoformat(a["attempt_date"]) for a in chosen]
    intervals = [(b - a).days for a, b in zip(days, days[1:])]
    matching = [x for x in report["request_history"] if x["application_id"] == args.application
                and x["subject_ref"] == args.subject]
    if len(matching) != 1 or intervals != matching[0]["attempt_intervals_days"]:
        raise ValueError("Selected raw request intervals disagree")
    print(json.dumps({"scope": "raw-source counts and request arithmetic only", "batches": checks,
                      "application": args.application, "subject": args.subject,
                      "attempt_dates": [d.isoformat() for d in days], "interval_days": intervals}, indent=2))


if __name__ == "__main__":
    main()
