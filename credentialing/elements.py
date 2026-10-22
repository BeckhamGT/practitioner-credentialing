"""Independent element facts. Unknown intake and admission stay unprojectable."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

from .review import (anniversary, date_window, first_receipt_context, indexed,
                     latest_applications, metadata, peer_checks, read_rows, source_class)
from .timeline import decision_history, differences, load_contract
from .validation import GroundworkError, confined_file, digest, read_json


def day(value):
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise GroundworkError("element_date", "Invalid calendar date; no date inferred") from exc


def load_element_rules(path: Path, expected_sha, as_of):
    if path.is_symlink() or path.parent.is_symlink():
        raise GroundworkError("unsafe_path", "Element rule path cannot be symlinked")
    root = path.parent.resolve(strict=True)
    raw = confined_file(root, path.name).read_bytes()
    if digest(raw) != expected_sha:
        raise GroundworkError("policy_hash", "Element rule transcription differs from pinned hash")
    rules = read_json(raw)
    if (rules.get("format") != "credentialing-element-rules/1" or rules.get("gap_days") != 30
            or rules.get("long_gap_days") != 180 or rules.get("experience_years") != 5):
        raise GroundworkError("element_rules", "Unknown element rule contract")
    continuation = confined_file(root, rules["continuation_path"])
    contract, policy = load_contract(continuation, rules["continuation_sha256"], as_of)
    for source in rules["sources"].values():
        if source["effective_from"] is not None and source["effective_from"] > as_of:
            raise GroundworkError("future_policy", "Element source is not effective at export")
        if digest(confined_file(root, source["path"]).read_bytes()) != source["sha256"]:
            raise GroundworkError("policy_hash", "Element source text changed")
    return rules, contract, policy


def gap_intervals(history_rows, as_of, minimum=30):
    """P §3 Check 2: inclusive union after one unambiguous school completion."""
    schools = {row["to_date"] for row in history_rows if row["entry_type"] == "medical-school"}
    if len(schools) != 1 or "" in schools:
        return {"evaluated": False, "reason": "professional-school completion missing/ambiguous", "gaps": []}
    finish = day(next(iter(schools)))
    start, end = finish + timedelta(days=1), day(as_of)
    intervals = []
    for row in history_rows:
        lower, upper = day(row["from_date"]), day(row["to_date"]) or end
        if lower is None:
            return {"evaluated": False, "reason": "declared interval start missing", "gaps": []}
        if upper < lower:
            raise GroundworkError("element_date", "Declared interval runs backwards")
        if upper >= start and lower <= end:
            intervals.append((max(lower, start), min(upper, end)))
    gaps = []
    cursor = start
    for lower, upper in sorted(intervals):
        if lower > cursor:
            last = lower - timedelta(days=1)
            count = (last - cursor).days + 1
            if count >= minimum:
                gaps.append({"from": cursor.isoformat(), "to": last.isoformat(), "days": count})
        cursor = max(cursor, upper + timedelta(days=1))
    if cursor <= end and (end - cursor).days + 1 >= minimum:
        gaps.append({"from": cursor.isoformat(), "to": end.isoformat(), "days": (end - cursor).days + 1})
    return {"evaluated": True, "basis": "declared history only; not CV-reconciled or source-date-adopted",
            "school_finished": finish.isoformat(), "clock": as_of, "gaps": gaps}


def gap_explanations(result, docs, long_days):
    explanations = []
    for document in docs:
        fields = metadata(document["text"])
        period = re.fullmatch(r"([0-9]{4}-[0-9]{2}-[0-9]{2}) to ([0-9]{4}-[0-9]{2}-[0-9]{2})", fields.get("Period explained", ""))
        if period:
            lower, upper = map(day, period.groups())
            if upper < lower:
                raise GroundworkError("element_date", "Explanation period runs backwards")
            explanations.append({"from": lower.isoformat(), "to": upper.isoformat(), "source": document["source"], "metadata": fields})
    for gap in result["gaps"]:
        matches = [e for e in explanations if e["from"] <= gap["from"] and e["to"] >= gap["to"]]
        gap.update(explanations_covering_whole_interval=matches,
                   written_explanation_observed=bool(matches), requires_clinical_director=gap["days"] >= long_days,
                   explanation_adequacy="reserved-human-judgment")
    return result


def wa_observation(application, tables, declarations, as_of):
    app = application["row"]
    values = [app[k] for k in ("last_name", "first_name", "middle_name", "birth_year")]
    if not app["last_name"] or not app["first_name"] or not app["birth_year"]:
        return {"matched": None, "reason": "join identity incomplete", "observations": []}
    matches = [o for o in tables["licence-lookup-wa.csv"]
               if [o["row"][k] for k in ("lastname", "firstname", "middlename", "birthyear")] == values]
    grouped = defaultdict(list)
    for o in matches:
        grouped[o["source"]["batch"]].append(o)
    if any(len(items) > 1 for items in grouped.values()):
        return {"matched": None, "reason": "Washington join ambiguous in a batch", "observations": matches}
    latest = max(matches, key=lambda o: (o["row"]["lookup_date"], o["source"]["batch"])) if matches else None
    row = latest["row"] if latest else None
    declared = [d for d in declarations if d["row"]["credential_class"] == "licence"
                and d["row"]["jurisdiction_or_board"] == "WA"]
    return {"matched": bool(matches), "observations": matches, "latest_observation": latest,
            "no_WA_credential_in_export": not matches,
            "active_status_on_observation": row["status"] == "ACTIVE" if row else None,
            "unexpired_at_export_from_recorded_expiry": (day(row["expirationdate"]) >= day(as_of)) if row and row["expirationdate"] else None,
            "actiontaken_recorded": row["actiontaken"] if row else None,
            "board_reply_review_needed": row["actiontaken"] in ("Yes", "Pending") if row else None,
            "declared_WA_rows": declared,
            "recorded_board_number_declared": any(d["row"]["number_declared"] == row["credentialnumber"] for d in declared) if row else None,
            "full_unrestricted_conclusion": "not-inferred-from-actiontaken",
            "rule": "E Washington four-field join and missing-row convention; P §3 Check 1; lookup is not NPI"}


def entry_observations(app_id, current, entries, all_entries, versions, replies, policy, as_of, anchor):
    result = []
    first = day(anchor)
    window = anniversary(first, -5) if first else None
    for occurrence in entries:
        row = occurrence["row"]
        related = [r for r in replies if r["row"]["application_id"] == app_id and r["row"]["entry_id"] == row["entry_id"]]
        observations = []
        for response in related:
            value = response["row"]
            known_versions = [v for v in versions if v["source"]["batch"] <= response["source"]["batch"]
                              and v["row"]["received_date"] and v["row"]["received_date"] <= value["received_date"]]
            previous = max(known_versions, key=lambda v: int(v["row"]["revision"])) if known_versions else None
            contexts = [e for e in all_entries if e["row"]["application_id"] == app_id and e["row"]["entry_id"] == row["entry_id"]
                        and previous and e["row"]["revision"] == previous["row"]["revision"]]
            at_reply = contexts[0] if len(contexts) == 1 else None
            classification, citation = source_class(value, at_reply["row"] if at_reply else None, policy)
            observations.append({"source": response["source"], "row": value,
                                 "declared_context_at_reply": at_reply,
                                 "source_class": classification, "rule": citation,
                                 "within_export_receipt_window": date_window(value["received_date"], anchor, as_of),
                                 "confirmed_outcome": value["outcome"] == "confirmed",
                                 "dates_equal_current_declaration": value["verified_from"] == row["from_date"] and value["verified_to"] == row["to_date"],
                                 "entry_changes_since_reply_context": differences(at_reply["row"], row, ("revision",)) if at_reply else None,
                                 "reuse_after_reconciliation": "not-evaluated:G2"})
        lower, upper = day(row["from_date"]), day(row["to_date"]) or day(as_of)
        overlap = (upper >= window and lower <= day(as_of)) if window and lower else None
        result.append({"declared": occurrence, "is_education_entry": row["entry_type"] in ("medical-school", "residency", "fellowship", "other"),
                       "overlaps_five_year_floor": overlap,
                       "five_year_floor_start": window.isoformat() if window else None,
                       "floor_anchor": anchor or None,
                       "deeper_verification_may_be_required_for_conflict": True,
                       "reply_occurrences": observations, "any_reply_observed": bool(related),
                       "verification_conclusion": "not-evaluated:reconciliation-and-current-entry-scope"})
    return result


def completed_months(start, end, months):
    if not start or not end or months is None:
        return None
    lower, upper = day(start), day(end)
    target = lower.year * 12 + lower.month - 1 + months
    try:
        finish = date(target // 12, target % 12 + 1, lower.day) - timedelta(days=1)
    except ValueError:
        return None  # No implicit month-end/leap-day convention.
    return upper >= finish


def certification_observations(app_id, declarations, replies, policy, as_of, anchor):
    results = []
    for declaration in declarations:
        d = declaration["row"]
        if d["credential_class"] != "certification":
            continue
        for occurrence in replies:
            row = occurrence["row"]
            if row["application_id"] != app_id or row["declaration_id"] != d["declaration_id"]:
                continue
            cls, citation = source_class(row, d, policy, True)
            results.append({"declaration": declaration, "reply": occurrence, "source_class": cls, "rule": citation,
                            "within_export_receipt_window": date_window(row["received_date"], anchor, as_of),
                            "active_at_export_from_board_fields": row["certification_status"] == "Active"
                            and (not row["expiry_date"] or day(row["expiry_date"]) >= day(as_of)),
                            "non_expiring": row["expiry_date"] == "", "original_notes": row["notes"]})
    return results


def other_licence_observations(declarations, tables, as_of):
    results = []
    for declaration in declarations:
        d = declaration["row"]
        if d["credential_class"] != "licence" or d["jurisdiction_or_board"] == "WA":
            continue
        replies = [o for o in tables["licence-lookup-other-states.csv"]
                   if o["row"]["board_state"] == d["jurisdiction_or_board"] and o["row"]["licence_number"] == d["number_declared"]]
        results.append({"declaration": declaration, "board_observations": replies,
                        "missing_reply_is_no_licence": False,
                        "observations": [{"source": o["source"], "issuer_online_verification_label_matches": o["row"]["verified_by"] == d["issuer"] + " online verification",
                                          "unexpired_at_export_by_recorded_date": day(o["row"]["expiry_date"]) >= day(as_of) if o["row"]["expiry_date"] else None,
                                          "disciplinary_action_recorded": o["row"]["disciplinary_action"],
                                          "status_recorded": o["row"]["status"]} for o in replies]})
    return results


def direct_work_assertion(text):
    """Read explicit returned assertions; unfamiliar/negated prose is not a pass."""
    value = text.casefold()
    if re.search(r"\b(?:not|never) (?:worked|work|supervised)\b", value):
        return False
    if (re.search(r"\bi (?:have )?worked directly with (?:the )?applicant\b", value)
            or (re.search(r"\bwe (?:have )?worked in the same department\b", value)
                and re.search(r"\bi supervised\b.*\bapplicant.s cases\b", value))):
        return True
    return None


def privilege_components(requests, certs, entry_checks, rules, as_of):
    result = []
    for request in requests:
        row = request["row"]
        criterion = rules["criteria"].get(row["privilege_code"])
        if not criterion:
            result.append({"request": request, "published_code": False, "support_conclusion": None})
            continue
        supporting, eligibility = [], []
        for c in certs:
            value = c["reply"]["row"]
            pairs = criterion["certifications"]
            matches = any(code == value["board_code"] and specialty is not None
                          and specialty == value["certificate_specialty"] for code, specialty in pairs)
            accepted = c["source_class"] in ("listed-primary-class", "listed-equivalent-class") and c["within_export_receipt_window"] == "within-date-window-only"
            if matches and accepted and c["active_at_export_from_board_fields"]:
                supporting.append(c["reply"])
            if matches and accepted and value["certification_status"] == "Board eligible":
                eligibility.append({"reply": c["reply"], "group_permits_eligible": row["privilege_code"] in rules["board_eligible_groups"],
                                    "end_date_future": value["expiry_date"] > as_of if value["expiry_date"] else None,
                                    "candidate_in_good_standing_written_confirmation": "requires-reading-actual-board-wording"})
        training = []
        for label, months in criterion["training"]:
            matches = []
            for entry in entry_checks:
                for observation in entry["reply_occurrences"]:
                    value = observation["row"]
                    if value["verified_credential"] == label:
                        matches.append({"source": observation["source"], "reply_id": value["reply_id"],
                                        "source_class": observation["source_class"], "outcome": value["outcome"],
                                        "minimum_calendar_months": months,
                                        "recorded_duration_meets_minimum": completed_months(value["verified_from"], value["verified_to"], months),
                                        "dates_equal_current_declaration": observation["dates_equal_current_declaration"],
                                        "entry_changes_since_reply_context": observation["entry_changes_since_reply_context"],
                                        "accreditation_separately_stated": None,
                                        "accreditation_limit": "Returned title/completion is retained; no separate accreditation field or inferred accreditation pass"})
            training.append({"required_returned_title": label, "minimum_months": months, "observations": matches})
        result.append({"request": request, "published_code": True,
                       "criteria_version_matches": row["criteria_version_cited"] == rules["criteria_version"],
                       "criterion": criterion, "active_matching_certification_observations": supporting,
                       "board_eligible_observations": eligibility, "training_components": training,
                       "support_conclusion": None,
                       "limits": ["Component evidence, not final privilege support or clinical competency",
                                  "Training reconciliation/accreditation evidence and G6 one-component wording remain explicit",
                                  "Current experience belongs to clinical leadership; no automatic refusal from it"]})
    return result


def decision_conditions(register):
    """Inspect later independent conditions without leapfrogging unknown packet facts."""
    result = []
    earlier = []
    for record in register:
        fields = record["recorded_fields"]
        matching_prior = [d for d in earlier if d["recorded_fields"]["Application"] == fields["Application"]
                          and d["recorded_fields"]["Revision"] == fields["Revision"]
                          and d["recorded_fields"]["Body"] == fields["Body"] == "Governing Body"]
        no_reason_needed = fields["Outcome"] in ("approved", "recommended")
        reason_ok = no_reason_needed or bool(fields.get("Reason", "").strip())
        literal_supersedes = fields.get("Supersedes", "")
        prior_ids = [d["decision_id"] for d in matching_prior]
        result.append({**record,
                       "not_evaluated": ["same prior presentable packet", "final admission and supersession applicability"],
                       "condition_observations": {
                           "1_body_authority": record["authority_checks"]["body_may_record_outcome"],
                           "2_signatory_role": record["authority_checks"]["signatory_role_on_recorded_date"],
                           "3_recorded_revision_matches": None if record["recorded_revision_at_decision_date"] is None else fields["Revision"] == record["recorded_revision_at_decision_date"],
                           "3_same_presentable_packet_identity": None,
                           "4_prior_presentable_packet": None,
                           "5_reason_requirement_satisfied": reason_ok,
                           "5_reason_exemption": "plain approval or positive recommendation" if no_reason_needed else None,
                           "supersession_prior_GB_records_received": prior_ids,
                           "supersession_reference_recorded": literal_supersedes or None,
                           "supersession_reference_names_prior_received_record": literal_supersedes in prior_ids if literal_supersedes else None,
                           "supersession_admissibility": None if matching_prior else "no earlier same-body record received",
                       },
                       "evaluation_blocked_by": [] if record["admitted"] is False else ["G1/G2-dependent packet identity and prior presentability"],
                       "later_observation_is_not_first_refusal": True})
        earlier.append(record)
    return result


def assess_elements(store, state_sha, rules_path, rules_sha):
    retained = store.at(state_sha)
    manifest = retained["state"]["manifest"];as_of = manifest["as_of"]
    rules, contract, policy = load_element_rules(rules_path, rules_sha, as_of)
    tables, documents = read_rows(store, retained)
    apps = latest_applications(tables["applications.csv"])
    entries = indexed(tables["declared-history.csv"], "application_id", "revision")
    declared = indexed(tables["declared-credentials.csv"], "application_id", "revision")
    requests = indexed(tables["privilege-requests.csv"], "application_id", "revision")
    disclosures = indexed(tables["application-disclosures.csv"], "application_id", "revision")
    cases = []
    for app_id, application in sorted(apps.items()):
        app = application["row"];key = (app_id, app["revision"])
        history = entries.get(key, []);credentials = declared.get(key, [])
        source_docs = [d for d in documents if metadata(d["text"]).get("Application") == app_id]
        anchor, anchor_check = first_receipt_context(tables["applications.csv"], app_id)
        version_rows = [v for v in tables["applications.csv"] if v["row"]["application_id"] == app_id]
        checks = entry_observations(app_id, application, history, tables["declared-history.csv"], version_rows,
                                    tables["verification-replies.csv"], policy, as_of, anchor)
        gaps = gap_explanations(gap_intervals([h["row"] for h in history], as_of, rules["gap_days"]), source_docs, rules["long_gap_days"])
        certs = certification_observations(app_id, credentials, tables["certification-replies.csv"], policy, as_of, anchor)
        peers = []
        for occurrence in tables["peer-reference-replies.csv"]:
            row = occurrence["row"]
            if row["application_id"] != app_id:
                continue
            fields = peer_checks(row, app["discipline"], as_of, policy["peer_years"])
            direct = direct_work_assertion(row["relationship_stated"])
            criteria = [fields["same_discipline"], fields["box_says_not_related_or_partner"],
                        fields["worked_together_recency_from_returned_dates"], direct]
            returned_eligibility = False if any(v is False for v in criteria) else True if all(v is True for v in criteria) else None
            # Preserve prose for reading; never infer absence of a disqualifier from silence.
            peers.append({"reply": occurrence, "field_checks": fields,
                          "relationship_prose": row["relationship_stated"],
                          "explicit_direct_work_assertion": direct,
                          "eligible_on_returned_relationship_fields": returned_eligibility,
                          "explicit_disqualification_in_box": row["related_or_partner"] == "Yes",
                          "full_qualification": None,
                          "currency_basis": "export only; no admissible presentation inferred"})
        ppq = disclosures.get(key, [])
        high_risk = [q for q in ppq if q["row"]["answer"] == "Yes"]
        documents_read = []
        for d in source_docs:
            fields = metadata(d["text"])
            disposition = d["source"]["path"].startswith("dispositions/")
            cd = rules["clinical_director"]
            actor_valid = (fields.get("Recorded by") == cd["recorded_by"] and fields.get("Date") is not None
                           and cd["from"] <= fields["Date"] <= cd["to"]) if disposition else None
            documents_read.append({"source": d["source"], "metadata": fields,
                                   "text": d["text"], "clinical_director_authority_prefix": actor_valid,
                                   "binding_and_effect": "not-adopted-automatically; retain source claims and scoped anomalies"})
        cases.append({"application_id": app_id, "revision": int(app["revision"]), "application_source": application["source"],
                      "first_receipt_anchor": anchor or None, "anchor_check": anchor_check,
                      "intake_evidence": {"application_signature_date_and_revision_evidence": None,
                                          "current_CV_content_and_reconciliation": None,
                                          "release_signed_date_recorded": app["release_signed_date"] or None,
                                          "cv_received_date_recorded": app["cv_received_date"] or None,
                                          "professional_question_rows": ppq,
                                          "expected_question_codes_present": set(q["row"]["question_code"] for q in ppq) == set(rules["practice_question_codes"]),
                                          "all_exported_questions_answered_yes_or_no": all(q["row"]["answer"] in ("Yes", "No") for q in ppq) if ppq else None,
                                          "every_observed_yes_has_comment": all(bool(q["row"]["applicant_comment"].strip()) for q in high_risk),
                                          "high_risk_yes_observed": high_risk},
                      "licensure_observations": wa_observation(application, tables, credentials, as_of),
                      "other_licence_observations": other_licence_observations(credentials, tables, as_of),
                      "declared_history_gaps": gaps, "entry_evidence": checks,
                      "certification_observations": certs,
                      "privilege_components": privilege_components(requests.get(key, []), certs, checks, rules, as_of),
                      "peer_observations": peers, "actual_documents_read": documents_read,
                      "schema_projection": {"status": None, "packet_presentable": None,
                                            "positive_decision_admission": None, "activation": None},
                      "evidence_tasks": [{"item": "Obtain signed/dated application and CV tied to this revision, or explicit authorized export representation; reconcile CV against application/verifications.",
                                          "owner": "Medical Services Professional", "due": None}],
                      "limits": "Independent facts only; no applicant failure inferred from unavailable export evidence"})
    decisions = decision_conditions(decision_history(tables, documents, policy))
    return {"format": "credentialing-element-assessment/1", "scope": "independent-facts-with-unresolved-schema-projection",
            "batch": manifest["batch"], "as_of": as_of, "state_sha256": state_sha,
            "previous_state_sha256": retained["state"]["previous_state_sha256"],
            "rules_sha256": rules_sha, "rule_sources": {**policy["sources"], **rules["sources"], "E": contract["export_guide"]},
            "assessed_snapshot_written": False, "schema_representation": "blocked-not-partial-or-deferred",
            "representation_conflicts": ["Required status has no truthful unresolved-intake enum",
                                         "packet_presentable requires a known boolean", "admitted requires a first-failed-condition refusal or supported admission"],
            "applications": cases, "decision_conditions": decisions,
            "summary": {"applications": len(cases), "declared_gaps_at_least_30_days": sum(len(c["declared_history_gaps"]["gaps"]) for c in cases),
                        "long_gaps_at_least_180_days": sum(g["requires_clinical_director"] for c in cases for g in c["declared_history_gaps"]["gaps"]),
                        "decisions_received": len(decisions), "proven_early_refusals": sum(d["admitted"] is False for d in decisions),
                        "admission_evaluation_blocked": sum(d["admitted"] is None for d in decisions)}}
