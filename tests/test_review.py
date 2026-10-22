"""Independent record checks; synthetic fixtures never assert full business outcomes."""

import copy
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest.mock import patch

from credentialing.cli import main
from credentialing.review import (authority_checks, date_window, load_policy, metadata,
                                 peer_checks, review, source_class, first_receipt_context)
from credentialing.storage import Store
from credentialing.validation import GroundworkError, digest, load_batch
from tests.test_groundwork import csv_bytes, fixture, rehash

POLICY_ROOT = Path(__file__).resolve().parents[1] / "references" / "record-review"
POLICY_SHA = digest((POLICY_ROOT / "rules.json").read_bytes())


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.policy = load_policy(POLICY_ROOT, POLICY_SHA, "2026-03-16")

    def expect_error(self, code, call):
        with self.assertRaises(GroundworkError) as caught:
            call()
        self.assertEqual(caught.exception.code, code)

    def decision(self, **overrides):
        fields = {"Decision ID": "SYNTH-DECISION", "Body": "Governing Body", "Outcome": "approved",
                  "Signatory": "Ms. Corinne Batiste", "Role": "Chair, Governing Body",
                  "Application": "SYNTH-001", "Revision": "1", "Decision date": "2026-03-16"}
        return {**fields, **overrides}

    def peer(self, **overrides):
        row = {"signature_date": "2024-03-16", "last_worked_together_end": "", "related_or_partner": "No",
               "referee_specialty_stated": "Family Medicine", "recommendation": "Do not recommend"}
        return {**row, **overrides}

    def build_state(self, batch=1, previous=None, store=None):
        root = self.root / f"input-{batch}"
        manifest = fixture(root, batch, {1: "2026-03-16", 2: "2026-04-20"}[batch])
        store = store or Store(self.root / "state")
        parsed, raw, contents, _ = load_batch(root, batch)
        receipt = store.stage(parsed, raw, contents, previous)
        return root, manifest, store, receipt["state_sha256"]

    def test_policy_pin_and_each_retained_source_hash_are_enforced(self):
        self.expect_error("policy_hash", lambda: load_policy(POLICY_ROOT, "0" * 64, "2026-03-16"))
        local = self.root / "policies"
        local.mkdir()
        for file in POLICY_ROOT.iterdir():
            (local / file.name).write_bytes(file.read_bytes())
        (local / "authority.txt").write_text("altered source")
        self.expect_error("policy_hash", lambda: load_policy(local, POLICY_SHA, "2026-03-16"))

    def test_future_policy_is_never_applied_to_earlier_export(self):
        self.expect_error("future_policy", lambda: load_policy(POLICY_ROOT, POLICY_SHA, "2025-12-31"))

    def test_applicant_delivery_overrides_authentic_looking_registrar_claim(self):
        row = {"received_from": "Applicant — hand-delivered at intake", "element": "education-and-training",
               "attester_organization": "Synthetic Medical School", "attester_role": "Registrar"}
        context = {"organization": "Synthetic Medical School", "entry_type": "medical-school"}
        self.assertEqual(source_class(row, context, self.policy)[0], "applicant-carried")

    def test_primary_office_requires_matching_declared_organization_and_type(self):
        row = {"received_from": "Registrar's office — Synthetic Medical School", "element": "education-and-training",
               "attester_organization": "Synthetic Medical School"}
        context = {"organization": "Synthetic Medical School", "entry_type": "medical-school"}
        self.assertEqual(source_class(row, context, self.policy)[0], "listed-primary-class")
        self.assertEqual(source_class(row, {**context, "organization": "Another School"}, self.policy)[0], "needs-source-review")
        self.assertEqual(source_class(row, {**context, "entry_type": "residency"}, self.policy)[0], "needs-source-review")

    def test_nonlisted_society_and_unresolved_secondary_route_are_not_promoted(self):
        context = {"organization": "Synthetic Medical School", "entry_type": "medical-school"}
        row = {"received_from": "State medical society — Synthetic Society", "element": "education-and-training",
               "attester_organization": "Synthetic Society"}
        self.assertEqual(source_class(row, context, self.policy)[0], "not-on-accepted-list")
        row["received_from"] = "Medical staff office — Most Recent Affiliation"
        row["notes"] = "The school did not answer three requests."
        self.assertEqual(source_class(row, context, self.policy)[0], "needs-source-review")

    def test_missing_link_does_not_become_a_pass(self):
        self.assertEqual(source_class({"received_from": "Registrar's office — School"}, None, self.policy)[0], "needs-link-review")

    def test_board_delivery_is_checked_against_issuer_code_and_credential_class(self):
        row = {"received_from": "Certifying board — Board", "board_name": "Board", "board_code": "BOARD"}
        context = {"issuer": "Board", "jurisdiction_or_board": "BOARD", "credential_class": "certification"}
        self.assertEqual(source_class(row, context, self.policy, True)[0], "listed-primary-class")
        self.assertEqual(source_class(row, {**context, "credential_class": "licence"}, self.policy, True)[0], "needs-source-review")

    def test_first_receipt_inclusive_and_decision_day_strict_but_export_inclusive(self):
        self.assertEqual(date_window("2026-01-01", "2026-01-01", "2026-03-16"), "within-date-window-only")
        self.assertEqual(date_window("2026-03-16", "2026-01-01", "2026-03-16"), "within-date-window-only")
        self.assertEqual(date_window("2026-03-16", "2026-01-01", "2026-03-16", True), "after-or-at-decision")
        self.assertEqual(date_window("2025-12-31", "2026-01-01", "2026-03-16"), "before-first-receipt")
        self.assertEqual(date_window("2026-02-01", "", "2026-03-16"), "unknown-date")

    def test_peer_signature_anniversary_is_inclusive_and_next_day_is_stale(self):
        row = self.peer()
        on_day = peer_checks(row, "Family Medicine", "2026-03-16")
        after = peer_checks(row, "Family Medicine", "2026-03-17")
        self.assertTrue(on_day["signature_current_at_export_only"])
        self.assertFalse(after["signature_current_at_export_only"])
        self.assertEqual(on_day["qualification_conclusion"], "not-evaluated")

    def test_peer_disqualifiers_are_independent_and_missing_values_stay_unknown(self):
        row = self.peer(signature_date="2026-03-16", last_worked_together_end="2024-03-15", related_or_partner="Yes")
        result = peer_checks(row, "Psychiatry", "2026-03-16")
        self.assertFalse(result["same_discipline"])
        self.assertFalse(result["box_says_not_related_or_partner"])
        self.assertFalse(result["worked_together_recency_from_returned_dates"])
        missing = peer_checks(self.peer(signature_date="", related_or_partner=""), None, "2026-03-16")
        self.assertIsNone(missing["same_discipline"])
        self.assertIsNone(missing["box_says_not_related_or_partner"])
        self.assertIsNone(missing["signature_current_at_export_only"])

    def test_peer_blank_work_end_is_ongoing_but_future_last_work_date_does_not_pass(self):
        result = peer_checks(self.peer(signature_date="2026-03-16"), "Family Medicine", "2026-03-16")
        self.assertTrue(result["worked_together_recency_from_returned_dates"])
        result = peer_checks(self.peer(signature_date="2026-03-16", last_worked_together_end="2026-03-17"), "Family Medicine", "2026-03-16")
        self.assertFalse(result["worked_together_recency_from_returned_dates"])

    def test_peer_box_does_not_adjudicate_contradictory_relationship_text(self):
        row = self.peer(related_or_partner="No", relationship_stated="The applicant is my spouse.")
        result = peer_checks(row, "Family Medicine", "2026-03-16")
        self.assertTrue(result["box_says_not_related_or_partner"])
        self.assertEqual(result["relationship_text_assessment"], "not-evaluated")
        self.assertEqual(result["qualification_conclusion"], "not-evaluated")

    def test_leap_anniversary_without_policy_is_unknown_not_shifted(self):
        result = peer_checks(self.peer(signature_date="2024-02-29"), "Family Medicine", "2026-02-28")
        self.assertIsNone(result["signature_second_anniversary"])
        self.assertIsNone(result["signature_current_at_export_only"])

    def test_authority_passes_are_not_full_admission_or_approval_computed_by_tool(self):
        fields = self.decision()
        before = copy.deepcopy(fields)
        result = authority_checks(fields, self.policy)
        self.assertTrue(result["body_may_record_outcome"])
        self.assertTrue(result["signatory_role_on_recorded_date"])
        self.assertEqual(result["final_admission"], "not-evaluated")
        self.assertIn("prior packet readiness", result["remaining_checks"])
        self.assertEqual(fields, before)

    def test_mec_approval_fails_body_first_without_rewriting_recorded_outcome(self):
        fields = self.decision(**{"Body": "Executive Committee of the Medical Staff", "Signatory": "Dr. Peter Vandermolen, MD",
                                  "Role": "Chair, Executive Committee of the Medical Staff"})
        result = authority_checks(fields, self.policy)
        self.assertFalse(result["body_may_record_outcome"])
        self.assertTrue(result["signatory_role_on_recorded_date"])
        self.assertEqual(result["first_failed_authority_check"], "body-authority")
        self.assertEqual(fields["Outcome"], "approved")

    def test_claimed_signatory_role_is_checked_against_roster_not_record_claim(self):
        fields = self.decision(Signatory="Unknown Person")
        result = authority_checks(fields, self.policy)
        self.assertFalse(result["signatory_role_on_recorded_date"])
        self.assertEqual(result["first_failed_authority_check"], "signatory-role")

    def test_designee_requires_actual_designation_and_term_dates(self):
        fields = self.decision(Signatory="Mr. Desmond Ihejirika", Role="Vice-Chair, Governing Body")
        for day, expected in (("2026-01-04", False), ("2026-01-05", True), ("2026-12-31", True), ("2027-01-01", False)):
            with self.subTest(day=day):
                self.assertEqual(authority_checks({**fields, "Decision date": day}, self.policy)["signatory_role_on_recorded_date"], expected)

    def test_duplicate_metadata_is_not_silently_resolved(self):
        self.expect_error("review_document", lambda: metadata("**Outcome:** denied\n**Outcome:** approved\n"))

    def test_review_of_old_state_does_not_read_new_head_or_later_objects(self):
        _, _, store, first = self.build_state()
        _, _, _, second = self.build_state(2, first, store)
        later_state = store.root / "objects" / "states" / second
        later_blob = store.root / "objects" / "blobs" / store.current()["state"]["manifest_sha256"]
        read = Path.read_bytes
        def guarded(path):
            if path in (store.root / "HEAD.json", later_state, later_blob):
                raise AssertionError("A newer occurrence was read")
            return read(path)
        before = (store.root / "HEAD.json").read_bytes()
        with patch.object(Path, "read_bytes", guarded):
            result = review(store, first, POLICY_ROOT, POLICY_SHA)
        self.assertEqual(result["batch"], 1)
        self.assertEqual(result["state_sha256"], first)
        self.assertEqual((store.root / "HEAD.json").read_bytes(), before)

    def test_read_only_review_and_blocked_run_do_not_write_assessed_snapshots(self):
        _, _, store, first = self.build_state()
        before = {str(p.relative_to(store.root)): p.read_bytes() for p in store.root.rglob("*") if p.is_file()}
        result = review(store, first, POLICY_ROOT, POLICY_SHA)
        after = {str(p.relative_to(store.root)): p.read_bytes() for p in store.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.assertEqual(result["business_blockers"], ["G1", "G2"])
        self.assertFalse(result["assessed_snapshot_written"])
        self.assertNotIn("applications", result)
        self.assertIn("packet readiness", result["not_evaluated"])
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(["review", "--store", str(store.root), "--state", first,
                         "--policy", str(POLICY_ROOT), "--policy-sha256", POLICY_SHA])
        self.assertEqual(code, 0, stderr.getvalue())
        self.assertEqual(json.loads(stdout.getvalue())["state_sha256"], first)

    def test_blank_release_and_cv_do_not_suppress_independent_record_review(self):
        root, manifest, store, first = self.build_state()
        result = review(store, first, POLICY_ROOT, POLICY_SHA)
        self.assertEqual(result["scope"], "independent-record-checks-only")
        self.assertEqual(result["not_evaluated"][0], "completeness")

    def test_conflicting_first_receipt_is_not_resolved_using_latest_revision(self):
        rows = [{"row": {"application_id": "SYNTH-001", "revision": "1", "received_date": "2026-01-01", "first_received_date": "2026-01-01"}},
                {"row": {"application_id": "SYNTH-001", "revision": "2", "received_date": "2026-02-01", "first_received_date": "2026-02-01"}}]
        anchor, result = first_receipt_context(rows, "SYNTH-001")
        self.assertEqual(anchor, "")
        self.assertEqual(result, "missing-or-conflicting-first-receipt")

    def test_actual_report_path_preserves_discrepancy_without_deciding_it(self):
        root = self.root / "populated"
        manifest = fixture(root)
        entry = {"entry_id": "SYNTH-ENTRY", "application_id": "SYNTH-001", "revision": "1", "entry_type": "employment",
                 "organization": "Example Employer", "role": "Physician", "from_date": "2020-01-01", "to_date": ""}
        (root / "declared-history.csv").write_bytes(csv_bytes("declared-history.csv", [entry]))
        reply = {"reply_id": "SYNTH-REPLY", "application_id": "SYNTH-001", "entry_id": "SYNTH-ENTRY",
                 "element": "affiliation-and-employment", "attester_organization": "Example Employer",
                 "received_from": "Medical staff office — Example Employer", "received_date": "2026-03-16",
                 "outcome": "confirmed-with-discrepancy", "notes": "The declared date and verified date disagree."}
        (root / "verification-replies.csv").write_bytes(csv_bytes("verification-replies.csv", [reply]))
        for name in ("declared-history.csv", "verification-replies.csv"):
            rehash(root, manifest, name)
        store = Store(self.root / "populated-store")
        parsed, raw, contents, _ = load_batch(root, 1)
        sha = store.stage(parsed, raw, contents, None)["state_sha256"]
        report = review(store, sha, POLICY_ROOT, POLICY_SHA)
        check = report["source_reply_checks"][0]
        self.assertEqual(check["source_class_check"], "listed-primary-class")
        self.assertEqual(check["original_outcome"], "confirmed-with-discrepancy")
        self.assertEqual(check["recorded_notes"], reply["notes"])
        self.assertEqual(check["verification_conclusion"], "not-evaluated")
        self.assertEqual(check["source"]["csv_row"], 2)
        self.assertEqual(report["batch"], 1)


if __name__ == "__main__":
    unittest.main()
