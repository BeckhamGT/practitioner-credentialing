"""Synthetic tests; actual-case comparisons are separate generated evidence."""

import copy
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from credentialing.cli import main
from credentialing.elements import (assess_elements, completed_months, decision_conditions,
                                    direct_work_assertion, gap_explanations, gap_intervals,
                                    load_element_rules, wa_observation)
from credentialing.snapshots import verify_snapshot
from credentialing.storage import Store
from credentialing.validation import GroundworkError, digest, json_bytes, load_batch
from credentialing.writer import SnapshotWriter, snapshot_path
from tests.test_continuation import row
from tests.test_groundwork import fixture, rehash

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / "references/element-rules.json"
RULES_SHA = digest(RULES.read_bytes())


def history(kind, lower, upper, **extra):
    return {"entry_type": kind, "from_date": lower, "to_date": upper, **extra}


class ElementTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def test_inclusive_gap_union_merges_overlap_and_ongoing_entries(self):
        rows = [history("medical-school", "2010-01-01", "2013-06-30"),
                history("residency", "2013-07-01", "2016-06-30"),
                history("employment", "2016-06-15", "2020-12-31"),
                history("teaching", "2021-01-01", "")]
        self.assertEqual(gap_intervals(rows, "2026-03-16")["gaps"], [])

    def test_exact_30_day_gap_and_29_day_interval(self):
        base = [history("medical-school", "2010-01-01", "2013-06-30")]
        result = gap_intervals(base + [history("employment", "2013-07-31", "")], "2013-08-01")
        self.assertEqual(result["gaps"], [{"from": "2013-07-01", "to": "2013-07-30", "days": 30}])
        self.assertEqual(gap_intervals(base + [history("employment", "2013-07-30", "")], "2013-08-01")["gaps"], [])

    def test_recompute_whole_history_after_changed_date_without_adopting_source_value(self):
        rows = [history("medical-school", "2010-01-01", "2013-06-30"), history("employment", "2013-07-01", "2019-03-31"), history("employment", "2019-11-06", "")]
        result = gap_intervals(rows, "2026-03-16")
        self.assertEqual(result["gaps"][0]["days"], 219)
        rows[1]["to_date"] = "2019-11-05"
        self.assertEqual(gap_intervals(rows, "2026-03-16")["gaps"], [])

    def test_explanation_must_cover_whole_interval_and_long_gap_routes_without_judgment(self):
        value = {"gaps": [{"from": "2019-04-01", "to": "2019-11-05", "days": 219}]}
        small = {"text": "**Period explained:** 2019-04-02 to 2019-11-05\n", "source": {"path": "synthetic.md"}}
        self.assertFalse(gap_explanations(copy.deepcopy(value), [small], 180)["gaps"][0]["written_explanation_observed"])
        small["text"] = "**Period explained:** 2019-03-31 to 2019-11-06\n"
        result = gap_explanations(copy.deepcopy(value), [small], 180)["gaps"][0]
        self.assertTrue(result["written_explanation_observed"]);self.assertTrue(result["requires_clinical_director"])
        self.assertEqual(result["explanation_adequacy"], "reserved-human-judgment")

    def test_missing_or_ambiguous_school_completion_is_unknown(self):
        self.assertFalse(gap_intervals([], "2026-03-16")["evaluated"])
        self.assertFalse(gap_intervals([history("medical-school", "2010-01-01", "")], "2026-03-16")["evaluated"])

    def test_calendar_training_duration_and_unstated_month_end_convention(self):
        self.assertTrue(completed_months("2010-07-01", "2013-06-30", 36))
        self.assertFalse(completed_months("2010-07-01", "2013-06-29", 36))
        self.assertIsNone(completed_months("2024-02-29", "2025-02-28", 12))
        self.assertIsNone(completed_months("2010-07-01", "2013-06-30", None))

    def test_wa_exact_join_expiry_inclusive_and_npi_is_not_licence(self):
        app = {"row": {"last_name": "SYNTH", "first_name": "Example", "middle_name": "", "birth_year": "1980"}}
        board = {"row": {"lastname": "SYNTH", "firstname": "Example", "middlename": "", "birthyear": "1980", "lookup_date": "2026-03-16", "status": "ACTIVE", "expirationdate": "2026-03-16", "actiontaken": "No", "credentialnumber": "MD-SYNTH"}, "source": {"batch": 1}}
        result = wa_observation(app, {"licence-lookup-wa.csv": [board]}, [], "2026-03-16")
        self.assertTrue(result["matched"]);self.assertTrue(result["unexpired_at_export_from_recorded_expiry"])
        self.assertFalse(result["recorded_board_number_declared"])
        app["row"]["birth_year"] = ""
        self.assertIsNone(wa_observation(app, {"licence-lookup-wa.csv": []}, [], "2026-03-16")["matched"])

    def test_wa_missing_row_convention_does_not_apply_to_incomplete_join(self):
        app = {"row": {"last_name": "SYNTH", "first_name": "Example", "middle_name": "", "birth_year": "1980"}}
        self.assertTrue(wa_observation(app, {"licence-lookup-wa.csv": []}, [], "2026-03-16")["no_WA_credential_in_export"])

    def test_prose_assertion_is_read_without_promoting_unfamiliar_or_negated_text(self):
        self.assertTrue(direct_work_assertion("We worked in the same department and I supervised several of the applicant's cases."))
        self.assertFalse(direct_work_assertion("I never worked directly with the applicant."))
        self.assertIsNone(direct_work_assertion("I admire the applicant's reputation."))

    def test_reason_observation_does_not_leapfrog_unknown_prior_packet(self):
        def item(id_, reason, supersedes=""):
            return {"decision_id": id_, "recorded_fields": {"Application": "SYNTH", "Revision": "1", "Body": "Governing Body", "Outcome": "denied", "Reason": reason, "Supersedes": supersedes}, "recorded_revision_at_decision_date": "1", "authority_checks": {"body_may_record_outcome": True, "signatory_role_on_recorded_date": True}, "admitted": None}
        result = decision_conditions([item("SYNTH-1", ""), item("SYNTH-2", "Reason")])
        self.assertFalse(result[0]["condition_observations"]["5_reason_requirement_satisfied"])
        self.assertIsNone(result[0]["admitted"])
        self.assertEqual(result[1]["condition_observations"]["supersession_prior_GB_records_received"], ["SYNTH-1"])
        self.assertIsNone(result[1]["condition_observations"]["supersession_admissibility"])

    def test_pinned_sources_and_explicit_none_effective_date(self):
        rules, _, _ = load_element_rules(RULES, RULES_SHA, "2026-03-16")
        self.assertIsNone(rules["sources"]["APP"]["effective_from"])
        with self.assertRaises(GroundworkError):load_element_rules(RULES, "0" * 64, "2026-03-16")

    def test_actual_processing_path_keeps_internal_report_but_no_fake_snapshot(self):
        folder = self.root / "input";manifest = fixture(folder, document=True)
        document = folder / "letters/synthetic-note.md"
        document.write_text(document.read_text() + "\n**Application:** SYNTH-001\nUnicode source — preserved.\n")
        rehash(folder, manifest, "letters/synthetic-note.md")
        manifest, raw, contents, _ = load_batch(folder, 1)
        store = Store(self.root / "store");sha = store.stage(manifest, raw, contents, None)["state_sha256"]
        report = self.root / "assessment.json";out, err = io.StringIO(), io.StringIO()
        command = ["--store", str(store.root), "--state", sha, "--rules", str(RULES), "--rules-sha256", RULES_SHA]
        with redirect_stdout(out):
            self.assertEqual(main(["elements", *command]), 0)
        report.write_bytes(out.getvalue().encode())
        with redirect_stdout(out), redirect_stderr(err):
            code = main(["run", *command, "--report", str(report)])
        self.assertEqual(code, 3);self.assertEqual(json.loads(err.getvalue())["error"], "snapshot_unrepresentable")
        value = json.loads(report.read_bytes());self.assertIsNone(value["applications"][0]["schema_projection"]["status"])
        self.assertFalse(value["assessed_snapshot_written"])
        self.assertFalse((self.root / "deliverables/snapshots").exists())


class WriterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / "rules.md").write_text("SYNTHETIC fixture facts only")
        self.schema = read_schema = json.loads((ROOT / "snapshot.schema.json").read_text())
        self.writer = SnapshotWriter(self.root, read_schema)
        self.clocks = {1: "2026-03-16", 2: "2026-04-20", 3: "2026-05-18"}

    def candidate(self, batch, id_=None):
        app = {"application_id": "SYNTH-ONLY", "revision": 1, "status": "in-verification",
               "elements": {k: "outstanding" for k in ("licensure", "experience", "gaps", "education", "certification", "references")},
               "packet_presentable": False, "decisions": [{"decision_id": "SYNTH-D", "admitted": False, "reason": "body-authority"}],
               "approval_decision_id": None, "activation": None, "monitored_conditions": [],
               "action_queue": [{"item": "SYNTHETIC outstanding evidence", "owner": "Medical Services Professional", "due": None}]}
        return {"schema_version": "credentialing-snapshot/1", "snapshot_id": id_ or f"SYNTH-{batch}", "batch": batch,
                "as_of": self.clocks[batch], "predecessor": None, "consumed": {"record_files": ["SYNTH.csv"], "documents": []},
                "produced": [snapshot_path(batch)], "rules_file": "rules.md", "applications": [app]}

    def test_unknown_fields_block_before_creating_snapshot_or_control_paths(self):
        with self.assertRaises(GroundworkError):self.writer.publish([self.candidate(1)], self.clocks, ["G1/G2"])
        self.assertFalse((self.root / "deliverables").exists());self.assertFalse((self.root / ".local").exists())

    def test_chronological_continuation_then_unchanged_rerun_preserves_bytes(self):
        for batch in (1, 2, 3):self.writer.publish([self.candidate(batch)], self.clocks, [])
        result = verify_snapshot(self.root, snapshot_path(3), self.schema)
        self.assertEqual([s["batch"] for s in result["checked"]], [1, 2, 3])
        original = (self.root / snapshot_path(3)).read_bytes()
        out = self.writer.publish([self.candidate(3, "SYNTH-IGNORED-NEW-ID")], self.clocks, [])
        self.assertEqual(out["result"], "unchanged");self.assertEqual(original, (self.root / snapshot_path(3)).read_bytes())

    def test_changed_sealed_candidate_requires_all_downstream_and_new_ids(self):
        for batch in (1, 2, 3):self.writer.publish([self.candidate(batch)], self.clocks, [])
        candidate = self.candidate(1, "SYNTH-CORRECTED-1");candidate["applications"][0]["action_queue"][0]["item"] = "Changed synthetic fact"
        original = (self.root / snapshot_path(1)).read_bytes()
        with self.assertRaises(GroundworkError):self.writer.publish([candidate], self.clocks, [], reason="Synthetic correction")
        self.assertEqual(original, (self.root / snapshot_path(1)).read_bytes())

    def test_supersession_retains_exact_bytes_and_regenerates_entire_chain(self):
        for batch in (1, 2, 3):self.writer.publish([self.candidate(batch)], self.clocks, [])
        before = {b: (self.root / snapshot_path(b)).read_bytes() for b in (1, 2, 3)}
        candidates = [self.candidate(b, f"SYNTH-CORRECTED-{b}") for b in (1, 2, 3)]
        candidates[0]["applications"][0]["action_queue"][0]["item"] = "Corrected synthetic evidence"
        result = self.writer.publish(candidates, self.clocks, [], reason="Synthetic correction, never real applicant evidence")
        registry = json.loads((self.root / "deliverables/snapshots/history/index.json").read_bytes())
        for old in before.values():
            item = next(i for i in registry["occurrences"] if i["sha256"] == digest(old))
            self.assertEqual(old, (self.root / item["retained_path"]).read_bytes())
        self.assertEqual(len(result["retained"]), 3)
        self.assertEqual(len(verify_snapshot(self.root, snapshot_path(3), self.schema)["checked"]), 3)

    def test_wrong_clock_and_illegal_approval_status_are_rejected_preflight(self):
        c = self.candidate(1);c["as_of"] = "2026-03-17"
        with self.assertRaises(GroundworkError):self.writer.publish([c], self.clocks, [])
        c = self.candidate(1);c["applications"][0]["status"] = "active"
        with self.assertRaises(GroundworkError):self.writer.publish([c], self.clocks, [])
        self.assertFalse((self.root / snapshot_path(1)).exists())

    def test_failed_write_is_not_current_success_and_recovery_restores_prior_outputs(self):
        self.writer.publish([self.candidate(1)], self.clocks, [])
        before = (self.root / snapshot_path(1)).read_bytes()
        original = self.writer._atomic
        def fail(path, raw):
            if path == self.root / snapshot_path(2):raise OSError("SYNTHETIC injected filesystem failure")
            return original(path, raw)
        with patch.object(self.writer, "_atomic", side_effect=fail):
            with self.assertRaises(GroundworkError):self.writer.publish([self.candidate(2)], self.clocks, [])
        with self.assertRaises(GroundworkError):verify_snapshot(self.root, snapshot_path(1), self.schema)
        self.assertTrue(self.writer.recover()["prior_outputs_restored"])
        self.assertEqual(before, (self.root / snapshot_path(1)).read_bytes())
        self.assertFalse((self.root / snapshot_path(2)).exists())
        self.assertEqual(self.writer.publish([self.candidate(2)], self.clocks, [])["result"], "written")

    def test_changed_refusal_reason_cannot_be_silently_rewritten(self):
        self.writer.publish([self.candidate(1)], self.clocks, [])
        c = self.candidate(2);c["applications"][0]["decisions"][0]["reason"] = "Altered refusal"
        with self.assertRaises(GroundworkError):self.writer.publish([c], self.clocks, [])

    def test_output_changed_after_failure_needs_investigation_not_overwrite(self):
        self.writer.publish([self.candidate(1)], self.clocks, [])
        original = self.writer._atomic
        def fail(path, raw):
            if path == self.root / snapshot_path(2):raise OSError("SYNTHETIC injected failure")
            return original(path, raw)
        with patch.object(self.writer, "_atomic", side_effect=fail):
            with self.assertRaises(GroundworkError):self.writer.publish([self.candidate(2)], self.clocks, [])
        (self.root / "deliverables/run-log.md").write_text("External work after failure")
        with self.assertRaises(GroundworkError):self.writer.recover()
        self.assertEqual((self.root / "deliverables/run-log.md").read_text(), "External work after failure")
