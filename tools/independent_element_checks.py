"""Independent stdlib oracle over original batch files; no runtime imports.

Uses day-by-day set subtraction, rather than the Skill's interval-union algorithm.
It checks declared-history arithmetic and original four-field WA joins only.
It cannot establish a CV comparison, complete intake or packet presentability.
"""

import argparse
import csv
import hashlib
import json
from datetime import date, timedelta
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--reports", type=Path, required=True)
    args = parser.parse_args()
    prior_rows = {name: [] for name in ("applications.csv", "declared-history.csv", "licence-lookup-wa.csv")}
    results = []
    for batch in (1, 2, 3):
        folder = args.inputs / f"batch-{batch:02}"
        source_hashes = {}
        for name in prior_rows:
            raw = (folder / name).read_bytes()
            source_hashes[name] = hashlib.sha256(raw).hexdigest()
            with (folder / name).open(newline="") as stream:
                prior_rows[name].extend(csv.DictReader(stream))
        # A report occurrence must be explicitly selected, not guessed from globs.
        report_path = args.reports / json.loads((args.reports / "current.json").read_text())[str(batch)]
        report = json.loads(report_path.read_text())
        manifest_clock = json.loads((folder / "input.manifest.json").read_text())["as_of"]
        assert report["as_of"] == manifest_clock
        assert manifest_clock in (folder / "README.md").read_text()
        clock = date.fromisoformat(manifest_clock)
        latest = {}
        for row in prior_rows["applications.csv"]:
            if row["application_id"] not in latest or int(row["revision"]) > int(latest[row["application_id"]]["revision"]):
                latest[row["application_id"]] = row
        checks = []
        for observed in report["applications"]:
            app = latest[observed["application_id"]]
            history = [r for r in prior_rows["declared-history.csv"] if (r["application_id"], r["revision"]) == (app["application_id"], app["revision"])]
            schools = {r["to_date"] for r in history if r["entry_type"] == "medical-school"}
            if len(schools) != 1 or "" in schools:
                raise ValueError("Independent oracle needs an unambiguous school-completion boundary")
            start = date.fromisoformat(next(iter(schools))) + timedelta(days=1)
            universe = set(range(start.toordinal(), clock.toordinal() + 1))
            covered = set()
            for row in history:
                lower = date.fromisoformat(row["from_date"]).toordinal()
                upper = date.fromisoformat(row["to_date"] or report["as_of"]).toordinal()
                covered.update(range(max(lower, start.toordinal()), min(upper, clock.toordinal()) + 1))
            missing = sorted(universe - covered)
            runs = []
            for number in missing:
                if not runs or number != runs[-1][-1] + 1:
                    runs.append([])
                runs[-1].append(number)
            expected = [{"from": date.fromordinal(r[0]).isoformat(), "to": date.fromordinal(r[-1]).isoformat(), "days": len(r)} for r in runs if len(r) >= 30]
            got = [{k: r[k] for k in ("from", "to", "days")} for r in observed["declared_history_gaps"]["gaps"]]
            assert expected == got, (app["application_id"], expected, got)
            key = tuple(app[k] for k in ("last_name", "first_name", "middle_name", "birth_year"))
            matches = [r for r in prior_rows["licence-lookup-wa.csv"] if tuple(r[k] for k in ("lastname", "firstname", "middlename", "birthyear")) == key]
            assert bool(matches) == observed["licensure_observations"]["matched"]
            checks.append({"application_id": app["application_id"], "revision": int(app["revision"]), "gaps": expected, "WA_match_observed": bool(matches)})
        results.append({"batch": batch, "as_of": report["as_of"], "report": report_path.name,
                        "report_sha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
                        "new_batch_source_hashes": source_hashes, "checked": checks})
    print(json.dumps({"method": "Original CSVs; daily sets and four-field joins; no credentialing imports",
                      "limits": "Declared-history arithmetic only; not CV reconciliation or business outcomes", "results": results}, indent=2))


if __name__ == "__main__":
    main()
