"""Synthetic fixtures only. Actual output verification is recorded separately."""

import copy
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path
from contextlib import redirect_stdout

from credentialing.cli import main
from credentialing.conditional import activation, conditions, decision, packet, peer_extra_request, ELEMENTS
from credentialing.review import load_policy
from credentialing.snapshots import verify_snapshot
from credentialing.storage import Store
from credentialing.timeline import timeline, load_contract, request_history
from credentialing.validation import GroundworkError, LAYOUT, digest, json_bytes, load_batch
from tests.test_groundwork import csv_bytes, fixture, rehash, save_manifest

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / "references/continuation.json"
RULES_SHA = digest(RULES.read_bytes())
POLICY = ROOT / "references/record-review"


def row(name, **values):
    return {**{k: "" for k in LAYOUT[name].split(",")}, **values}


class ContinuationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = Store(self.root / "store")
        self.policy = load_policy(POLICY, digest((POLICY / "rules.json").read_bytes()), "2026-03-16")

    def expect_error(self, code, call):
        with self.assertRaises(GroundworkError) as found:
            call()
        self.assertEqual(found.exception.code, code)

    def input(self, batch, revision=None):
        clock = {1: "2026-03-16", 2: "2026-04-20", 3: "2026-05-18"}[batch]
        folder = self.root / f"batch-{batch}"
        manifest = fixture(folder, batch, clock)
        apps = [row("applications.csv", application_id="SYNTH-001", revision=str(revision or 1),
                    first_received_date="2026-03-01", received_date="2026-03-01" if batch == 1 else clock)] if batch == 1 or revision else []
        self.replace(folder, manifest, "applications.csv", apps)
        return folder, manifest

    def replace(self, folder, manifest, name, values):
        (folder / name).write_bytes(csv_bytes(name, values))
        rehash(folder, manifest, name)

    def stage(self, folder, batch, previous=None):
        manifest, raw, contents, _ = load_batch(folder, batch)
        return self.store.stage(manifest, raw, contents, previous)["state_sha256"]

    def fields(self, **changes):
        return {"Decision ID": "SYNTH-GB-1", "Body": "Governing Body", "Signatory": "Ms. Corinne Batiste",
                "Role": "Chair, Governing Body", "Application": "SYNTH-001", "Revision": "1",
                "Decision date": "2026-03-15", "Outcome": "approved", "Privileges": "PRIV-FM",
                "Reason": "", "Effective date": "", "Supersedes": "", **changes}

    def add_decision(self, folder, manifest, fields):
        name = "decisions/synthetic.md"
        (folder / "decisions").mkdir(exist_ok=True)
        text = "# SYNTHETIC decision\n\n" + "\n".join(f"**{k}:** {v}" for k, v in fields.items()) + "\n"
        (folder / name).write_text(text)
        manifest["files"].append({"path": name, "sha256": digest(text.encode()),
                                  "source_id": "synthetic-document-" + str(manifest["batch"]),
                                  "source_url": "https://example.org/synthetic/decision", "source_batch": manifest["batch"], "kind": "document"})
        self.replace(folder, manifest, "correspondence.csv", [row("correspondence.csv", letter_id="SYNTH-CORR", date=fields["Decision date"],
                     application_id=fields["Application"], document_path=name)])

    def facts(self, **changes):
        return {"application_id": "SYNTH-001", "revision": 1, "complete": True, "cv_reconciled": True,
                "elements": {name: {"state": "resolved", "nothing_owed": True} for name in ELEMENTS},
                "usable_verifications": True, "open_discrepancy": False, "last_needed_reply_date": "2026-03-14", **changes}

    def test_unknown_signature_or_cv_never_yields_a_packet_boolean(self):
        for field in ("complete", "cv_reconciled"):
            result = packet(self.facts(**{field: None}))
            self.assertIsNone(result["presentable"])
            self.assertTrue(result["unevaluated_dependencies"])

    def test_persistent_finding_can_be_presentable_without_rewriting_the_finding(self):
        facts = self.facts()
        facts["elements"]["licensure"] = {"state": "finding", "nothing_owed": True}
        facts["elements"]["certification"] = {"state": "finding", "nothing_owed": True}
        result = packet(facts)
        self.assertTrue(result["presentable"])
        self.assertEqual(result["retained_element_states"]["licensure"], "finding")

    def test_unresolved_finding_and_long_gap_hold_prevent_readiness(self):
        for state in ("finding", "routed-to-clinical-director", "eligibility-question", "return-incomplete", "discrepancy"):
            facts = self.facts()
            facts["elements"]["gaps"] = {"state": state, "nothing_owed": False}
            self.assertFalse(packet(facts)["presentable"])

    def test_packet_requires_all_explicit_dependencies_and_a_real_last_reply_date(self):
        facts = self.facts();del facts["elements"]["references"]
        self.expect_error("conditional_input", lambda: packet(facts))
        self.assertIsNone(packet(self.facts(last_needed_reply_date=None))["presentable"])

    def test_numeric_truthiness_and_invented_element_states_are_not_evidence(self):
        self.expect_error("conditional_input", lambda: packet(self.facts(complete=1)))
        facts = self.facts();facts["elements"]["gaps"]["state"] = "assumed"
        self.expect_error("conditional_input", lambda: packet(facts))

    def test_body_failure_precedes_role_and_missing_packet(self):
        fields = self.fields(Body="Executive Committee of the Medical Staff", Signatory="Unknown")
        self.assertEqual(decision(fields, self.policy, 1, None, []), {"admitted": False, "reason": "body-authority"})

    def test_role_failure_precedes_revision(self):
        fields = self.fields(Signatory="Unknown", Revision="9")
        self.assertEqual(decision(fields, self.policy, 1, None, [])["reason"], "signatory-role")

    def test_revision_failure_precedes_packet_dependency_and_unknown_stays_unknown(self):
        self.assertEqual(decision(self.fields(Revision="2"), self.policy, 1, None, [])["reason"], "applicant/revision")
        self.assertIsNone(decision(self.fields(), self.policy, 1, None, [])["admitted"])

    def test_packet_must_precede_decision_and_match_revision(self):
        p = packet(self.facts(last_needed_reply_date="2026-03-15"))
        self.assertEqual(decision(self.fields(), self.policy, 1, p, [])["reason"], "prior presentable packet")
        p["revision"] = 2
        self.assertEqual(decision(self.fields(), self.policy, 1, p, [])["reason"], "applicant/revision")

    def test_plain_approval_and_positive_recommendation_need_no_reason(self):
        p = packet(self.facts())
        self.assertTrue(decision(self.fields(), self.policy, 1, p, [])["admitted"])
        fields = self.fields(Body="Executive Committee of the Medical Staff", Signatory="Dr. Peter Vandermolen, MD",
                             Role="Chair, Executive Committee of the Medical Staff", Outcome="recommended")
        prior = [{"fields": fields, "result": {"admitted": True, "reason": None}}]
        self.assertTrue(decision(fields, self.policy, 1, p, prior)["admitted"])

    def test_deferral_denial_negative_recommendation_and_conditions_require_reason(self):
        p = packet(self.facts())
        for outcome in ("deferred-pending-information", "denied", "approved-with-conditions"):
            self.assertEqual(decision(self.fields(Outcome=outcome), self.policy, 1, p, [])["reason"], "outcome/reason")

    def test_second_gb_decision_requires_exact_prior_admitted_id(self):
        p = packet(self.facts());first = self.fields()
        prior = [{"fields": first, "result": decision(first, self.policy, 1, p, [])}]
        second = self.fields(**{"Decision ID": "SYNTH-GB-2"})
        self.assertEqual(decision(second, self.policy, 1, p, prior)["reason"], "supersession")
        second["Supersedes"] = "SYNTH-GB-1"
        self.assertTrue(decision(second, self.policy, 1, p, prior)["admitted"])

    def test_unknown_prior_admission_is_not_assumed_away(self):
        p = packet(self.facts())
        prior = [{"fields": self.fields(), "result": {"admitted": None}}]
        self.assertIsNone(decision(self.fields(), self.policy, 1, p, prior)["admitted"])

    def test_only_admitted_current_revision_gb_approval_activates(self):
        for admitted in (False, None):
            self.assertIsNone(activation(self.fields(), {"admitted": admitted}, 1, "2026-03-16", {"PRIV-FM"})["activation"])
        self.assertIsNone(activation(self.fields(), {"admitted": True}, 2, "2026-03-16", {"PRIV-FM"})["activation"])

    def test_exact_grants_future_start_and_cycle_end_are_preserved(self):
        fields = self.fields(**{"Effective date": "2026-04-01"})
        before = activation(fields, {"admitted": True}, 1, "2026-03-16", {"PRIV-FM", "PRIV-IM"})["activation"]
        self.assertFalse(before["active_at_export"])
        self.assertEqual(before["privileges"], ["PRIV-FM"])
        self.assertEqual(before["cycle_end"], "2027-03-31")
        self.assertTrue(activation(fields, {"admitted": True}, 1, "2026-04-01", {"PRIV-FM"})["activation"]["active_at_export"])

    def test_office_semicolon_grant_separator_preserves_exact_codes(self):
        fields = self.fields(Privileges="PRIV-FM; PRIV-HOSP")
        result = activation(fields, {"admitted": True}, 1, "2026-04-01", {"PRIV-FM", "PRIV-HOSP", "PRIV-IM"})
        self.assertEqual(result["activation"]["privileges"], ["PRIV-FM", "PRIV-HOSP"])

    def test_leap_cycle_and_unpublished_grant_need_explicit_handling(self):
        fields = self.fields(**{"Decision date": "2024-02-29"})
        self.assertFalse(activation(fields, {"admitted": True}, 1, "2024-02-29", {"PRIV-FM"})["evaluated"])
        self.expect_error("conditional_input", lambda: activation(self.fields(), {"admitted": True}, 1, "2026-03-16", {"PRIV-IM"}))

    def test_condition_needs_named_satisfaction_and_does_not_block_activation(self):
        owed = [{"condition": "SYNTH licence renewal evidence", "due": "2026-04-01"}]
        wrong = [{"condition": "Unrelated document", "date": "2026-03-20"}]
        result = conditions(owed, wrong, "2026-04-01")[0]
        self.assertFalse(result["satisfied"]);self.assertTrue(result["finding"])
        self.assertEqual(result["owner"], "Clinical Director");self.assertFalse(result["blocks_activation"])
        correct = [{"condition": owed[0]["condition"], "date": "2026-04-02"}]
        self.assertFalse(conditions(owed, correct, "2026-04-01")[0]["satisfied"])
        self.assertTrue(conditions(owed, correct, "2026-04-02")[0]["satisfied"])

    def test_unanswered_extra_reference_does_not_hold_met_element_or_count(self):
        waiting = peer_extra_request(True, False, False)
        self.assertFalse(waiting["holds_element"]);self.assertFalse(waiting["counts_as_reference"])
        self.assertEqual(peer_extra_request(True, True, False)["closure"], "no-longer-needed")
        self.assertIsNone(peer_extra_request(None, True, False)["closure"])
        self.assertIsNone(peer_extra_request(True, False, True)["counts_as_reference"])

    def test_three_stage_resume_retains_prior_reports_and_ignores_newer_head(self):
        a, _ = self.input(1);s1 = self.stage(a, 1)
        before = timeline(self.store, s1, RULES, RULES_SHA)
        b, _ = self.input(2);s2 = self.stage(b, 2, s1)
        c, _ = self.input(3);s3 = self.stage(c, 3, s2)
        self.assertEqual(before, timeline(self.store, s1, RULES, RULES_SHA))
        result = timeline(self.store, s3, RULES, RULES_SHA)
        self.assertEqual(result["predecessor_state_sha256"], s2)
        self.assertFalse(result["assessed_snapshot_written"])
        self.assertEqual(result["as_of"], "2026-05-18")

    def test_contact_only_change_is_retained_without_claiming_evidence_reuse(self):
        a, ma = self.input(1)
        history = row("declared-history.csv", entry_id="SYNTH-E", application_id="SYNTH-001", revision="1",
                      organization="Synthetic Hospital", role="Physician", contact_email="old@example.org")
        self.replace(a, ma, "declared-history.csv", [history]);s1 = self.stage(a, 1)
        b, mb = self.input(2, 2)
        history.update(revision="2", contact_email="new@example.org")
        self.replace(b, mb, "declared-history.csv", [history]);s2 = self.stage(b, 2, s1)
        record = timeline(self.store, s2, RULES, RULES_SHA)["application_revisions"][-1]
        change = record["restated_comparisons"]["declared-history.csv"]["changed"][0]
        self.assertEqual(set(change["fields"]), {"contact_email"})
        self.assertEqual(record["evidence_reuse_conclusion"], "not-evaluated")

    def test_permanent_attempts_raw_replies_and_day64_schedule(self):
        a, ma = self.input(1)
        attempts = [row("verification-attempts.csv", attempt_id=f"SYNTH-ATT-{i}", application_id="SYNTH-001",
                        element="peer-reference", subject_ref="SYNTH-REF", attempt_date=day, outcome="no reply")
                    for i, day in enumerate(["2026-01-01", "2026-01-22", "2026-02-12"])]
        self.replace(a, ma, "verification-attempts.csv", attempts)
        self.replace(a, ma, "peer-referees.csv", [row("peer-referees.csv", application_id="SYNTH-001", referee_id="SYNTH-REF", first_request_date="2026-01-01")])
        s1 = self.stage(a, 1);result = timeline(self.store, s1, RULES, RULES_SHA)["request_history"][0]
        self.assertEqual(result["attempt_intervals_days"], [21, 21])
        self.assertEqual(result["peer_day64_date"], "2026-03-06")
        self.assertTrue(result["no_returned_row_at_day64"])
        self.assertEqual(len(result["attempts"]), 3)
        b, mb = self.input(2)
        self.replace(b, mb, "peer-reference-replies.csv", [row("peer-reference-replies.csv", application_id="SYNTH-001", referee_id="SYNTH-REF", reply_id="SYNTH-REPLY", received_date="2026-04-01")])
        s2 = self.stage(b, 2, s1);after = timeline(self.store, s2, RULES, RULES_SHA)["request_history"][0]
        self.assertEqual(len(after["attempts"]), 3);self.assertTrue(after["reply_observed"])
        self.assertEqual(after["request_satisfied"], "not-evaluated")

    def test_missing_attempt_date_remains_unknown_not_zero_or_traceback(self):
        a, ma = self.input(1)
        self.replace(a, ma, "verification-attempts.csv", [row("verification-attempts.csv", application_id="SYNTH-001", element="peer-reference", subject_ref="SYNTH-REF")])
        result = timeline(self.store, self.stage(a, 1), RULES, RULES_SHA)["request_history"][0]
        self.assertIsNone(result["peer_day64_date"])

    def test_refused_body_record_remains_refused_across_three_batches(self):
        a, ma = self.input(1)
        self.add_decision(a, ma, self.fields(Body="Executive Committee of the Medical Staff"))
        s1 = self.stage(a, 1);before = timeline(self.store, s1, RULES, RULES_SHA)["decision_register"]
        b, _ = self.input(2);s2 = self.stage(b, 2, s1)
        c, _ = self.input(3);s3 = self.stage(c, 3, s2)
        after = timeline(self.store, s3, RULES, RULES_SHA)["decision_register"]
        self.assertEqual(before, after);self.assertFalse(after[0]["admitted"])
        self.assertEqual(after[0]["recorded_fields"]["Outcome"], "approved")

    def test_valid_authority_does_not_create_admission_or_activation(self):
        a, ma = self.input(1);self.add_decision(a, ma, self.fields())
        d = timeline(self.store, self.stage(a, 1), RULES, RULES_SHA)["decision_register"][0]
        self.assertIsNone(d["admitted"]);self.assertEqual(d["activation"], "not-evaluated")

    def test_unknown_revision_receipt_context_is_not_an_applicant_failure(self):
        a, ma = self.input(1)
        self.replace(a, ma, "applications.csv", [row("applications.csv", application_id="SYNTH-001", revision="1")])
        self.add_decision(a, ma, self.fields())
        d = timeline(self.store, self.stage(a, 1), RULES, RULES_SHA)["decision_register"][0]
        self.assertIsNone(d["admitted"])
        self.assertIsNone(d["first_failed_independent_condition"])

    def test_later_backdated_revision_does_not_rewrite_earlier_decision_check(self):
        a, ma = self.input(1);self.add_decision(a, ma, self.fields());s1 = self.stage(a, 1)
        before = timeline(self.store, s1, RULES, RULES_SHA)["decision_register"]
        b, mb = self.input(2, 2)
        app = row("applications.csv", application_id="SYNTH-001", revision="2", received_date="2026-03-10", first_received_date="2026-03-01")
        self.replace(b, mb, "applications.csv", [app]);s2 = self.stage(b, 2, s1)
        self.assertEqual(before, timeline(self.store, s2, RULES, RULES_SHA)["decision_register"])

    def test_contract_hash_future_effective_date_and_export_source_integrity(self):
        self.expect_error("policy_hash", lambda: load_contract(RULES, "0" * 64, "2026-03-16"))
        self.expect_error("future_policy", lambda: load_contract(RULES, RULES_SHA, "2026-03-15"))

    def test_timeline_cli_still_has_no_supplied_case_completeness_switch(self):
        a, _ = self.input(1);sha = self.stage(a, 1)
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(["timeline", "--store", str(self.store.root), "--state", sha,
                         "--rules", str(RULES), "--rules-sha256", RULES_SHA])
        self.assertEqual(code, 0);self.assertFalse(json.loads(output.getvalue())["assessed_snapshot_written"])


class SnapshotRelationshipTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name);(self.root / "rules.md").write_text("Synthetic rules fixture")
        self.schema = json.loads((ROOT / "snapshot.schema.json").read_text())

    def snapshot(self, batch, previous=None):
        path = f"synthetic-{batch}.json"
        app = {"application_id": "SYNTH-ONLY", "revision": 1, "status": "in-verification",
               "elements": {k: "outstanding" for k in ELEMENTS}, "packet_presentable": False,
               "decisions": [{"decision_id": "SYNTH-REFUSED", "admitted": False, "reason": "body-authority"}],
               "approval_decision_id": None, "activation": None, "monitored_conditions": [],
               "action_queue": [{"item": "Synthetic outstanding verification", "owner": "Medical Services Professional", "due": None}]}
        value = {"schema_version": "credentialing-snapshot/1", "snapshot_id": f"SYNTH-{batch}",
                 "batch": batch, "as_of": {1: "2026-03-16", 2: "2026-04-20", 3: "2026-05-18"}[batch],
                 "predecessor": {"path": previous, "sha256": digest((self.root / previous).read_bytes())} if previous else None,
                 "consumed": {"record_files": ["synthetic.csv"], "documents": []}, "produced": [path],
                 "rules_file": "rules.md", "applications": [app]}
        self.save(path, value)
        return path, value

    def save(self, path, value):
        (self.root / path).write_bytes(json_bytes(value))

    def fails(self, path):
        with self.assertRaises(GroundworkError):verify_snapshot(self.root, path, self.schema)

    def test_three_predecessors_are_verified_and_refusals_survive(self):
        p1, _ = self.snapshot(1);p2, _ = self.snapshot(2, p1);p3, _ = self.snapshot(3, p2)
        self.assertEqual([x["batch"] for x in verify_snapshot(self.root, p3, self.schema)["checked"]], [1, 2, 3])

    def test_predecessor_edit_is_not_silently_accepted(self):
        p1, v1 = self.snapshot(1);p2, _ = self.snapshot(2, p1)
        v1["snapshot_id"] = "SYNTH-ALTERED";self.save(p1, v1);self.fails(p2)

    def test_refusal_reason_or_received_history_cannot_be_rewritten(self):
        p1, _ = self.snapshot(1);p2, v2 = self.snapshot(2, p1)
        v2["applications"][0]["decisions"][0]["reason"] = "changed";self.save(p2, v2);self.fails(p2)

    def test_approval_cannot_point_to_refused_or_missing_record(self):
        p1, v = self.snapshot(1);v["applications"][0]["approval_decision_id"] = "SYNTH-REFUSED"
        self.save(p1, v);self.fails(p1)

    def test_invented_schema_status_and_missing_produced_self_are_rejected(self):
        p1, v = self.snapshot(1);v["applications"][0]["status"] = "G1-G2-pending";self.save(p1, v);self.fails(p1)
        v["applications"][0]["status"] = "in-verification";v["produced"] = ["rules.md"];self.save(p1, v);self.fails(p1)

    def test_schema_dates_use_real_calendar_and_workspace_paths_are_confined(self):
        p1, v = self.snapshot(1);v["as_of"] = "2026-02-30";self.save(p1, v);self.fails(p1)
        v["as_of"] = "2026-03-16";v["rules_file"] = "../escape.md";self.save(p1, v);self.fails(p1)
