"""Independent record checks. Never computes file readiness or decision admission."""

from __future__ import annotations

import csv
import io
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from .storage import Store
from .validation import (DAY, SHA, GroundworkError, confined_file, digest,
                         read_json, schema_validate)


POLICY_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["format", "sources", "peer_years", "body_outcomes", "roles",
                 "designated_education_sources", "designated_certification_sources"],
    "properties": {
        "format": {"const": "credentialing-record-review-rules/1"}, "peer_years": {"const": 2},
        "sources": {
            "type": "object", "additionalProperties": False, "required": ["P", "ATT", "AUTH"],
            "properties": {key: {
                "type": "object", "additionalProperties": False,
                "required": ["path", "sha256", "version", "effective_from", "url"],
                "properties": {"path": {"type": "string"}, "sha256": SHA, "version": {"type": "string", "minLength": 1},
                               "effective_from": DAY, "url": {"type": "string", "pattern": "^https://"}},
            } for key in ("P", "ATT", "AUTH")},
        },
        "body_outcomes": {"type": "object", "minProperties": 1,
                          "additionalProperties": {"type": "array", "minItems": 1, "uniqueItems": True,
                                                   "items": {"type": "string", "minLength": 1}}},
        "roles": {"type": "array", "minItems": 1, "items": {
            "type": "object", "additionalProperties": False,
            "required": ["body", "role", "name", "from", "to", "designation_from"],
            "properties": {**{key: {"type": "string", "minLength": 1} for key in ("body", "role", "name")},
                           "from": DAY, "to": DAY, "designation_from": {"oneOf": [DAY, {"type": "null"}]}},
        }},
        **{key: {"type": "array", "uniqueItems": True, "items": {"type": "string", "minLength": 1}}
           for key in ("designated_education_sources", "designated_certification_sources")},
    },
}


def load_policy(root: Path, expected_sha: str, as_of: str):
    if root.is_symlink():
        raise GroundworkError("unsafe_path", "Policy root cannot be a symlink")
    root = root.resolve(strict=True)
    raw = confined_file(root, "rules.json").read_bytes()
    if digest(raw) != expected_sha:
        raise GroundworkError("policy_hash", "Review rules differ from the explicitly pinned hash")
    policy = read_json(raw)
    schema_validate(policy, POLICY_SCHEMA)
    for source in policy["sources"].values():
        if source["effective_from"] > as_of:
            raise GroundworkError("future_policy", "Policy is not in force at this export date")
        text = confined_file(root, source["path"]).read_bytes()
        if digest(text) != source["sha256"]:
            raise GroundworkError("policy_hash", "Retained policy text differs from its pinned hash")
    return policy


def read_rows(store: Store, history: dict):
    """Keep each source occurrence, row number and batch; never collapse history."""
    tables = defaultdict(list)
    documents = []
    for _, state, _ in history["chain"]:
        manifest = state["manifest"]
        for source in manifest["files"]:
            provenance = {"batch": manifest["batch"], "path": source["path"], "sha256": source["sha256"],
                          "source_id": source["source_id"]}
            raw = store.blob(source["sha256"])
            if source["kind"] == "records":
                for number, row in enumerate(csv.DictReader(io.StringIO(raw.decode("utf-8"))), 2):
                    tables[source["path"]].append({"row": row, "source": {**provenance, "csv_row": number}})
            elif source["kind"] == "document":
                documents.append({"text": raw.decode("utf-8"), "source": provenance})
    return tables, documents


def indexed(rows, *fields):
    result = defaultdict(list)
    for occurrence in rows:
        result[tuple(occurrence["row"][field] for field in fields)].append(occurrence)
    return result


def latest_applications(rows):
    groups = defaultdict(list)
    for occurrence in rows:
        row = occurrence["row"]
        if not re.fullmatch(r"[1-9][0-9]*", row["revision"]):
            raise GroundworkError("review_identity", "Recorded revision is not a positive integer; no revision was guessed")
        groups[row["application_id"]].append(occurrence)
    result = {}
    for app, versions in groups.items():
        latest = max(int(v["row"]["revision"]) for v in versions)
        candidates = [v for v in versions if int(v["row"]["revision"]) == latest]
        if len(candidates) != 1:
            raise GroundworkError("review_identity", "Latest recorded revision is ambiguous; no value was selected")
        result[app] = candidates[0]
    return result


def first_receipt_context(rows, app_id):
    versions = [o for o in rows if o["row"]["application_id"] == app_id]
    first = [o for o in versions if o["row"]["revision"] == "1"]
    anchors = {o["row"]["first_received_date"] for o in versions}
    if len(first) != 1 or len(anchors) != 1 or "" in anchors:
        return "", "missing-or-conflicting-first-receipt"
    anchor = next(iter(anchors))
    if first[0]["row"]["received_date"] != anchor:
        return "", "first-revision-receipt-disagrees-with-anchor"
    return anchor, "consistent-first-receipt"


def source_class(row, context, policy, certification=False):
    """Classify a recorded delivery route; does not verify the claim's truth."""
    sender = row["received_from"]
    label, separator, organization = sender.partition(" — ")
    if label == "Applicant":
        return "applicant-carried", "ATT cross-cutting applicant prohibition; P §3"
    if context is None:
        return "needs-link-review", "ATT: source must correspond to the declared subject"
    if certification:
        if (label == "Certifying board" and separator and organization == row["board_name"]
                and context["credential_class"] == "certification"
                and context["issuer"] == row["board_name"]
                and context["jurisdiction_or_board"] == row["board_code"]):
            return "listed-primary-class", "ATT Board certification / Primary source"
        if sender in policy["designated_certification_sources"]:
            return "listed-equivalent-class", "ATT Board certification / Designated equivalent source"
    else:
        same_organization = (separator and organization == context["organization"]
                             and row["attester_organization"] == context["organization"])
        if row["element"] == "education-and-training":
            if same_organization and ((context["entry_type"] == "medical-school" and label in ("Registrar's office", "Dean's office"))
                                      or (context["entry_type"] in ("residency", "fellowship", "other")
                                          and label in ("Graduate medical education office", "Programme director"))):
                return "listed-primary-class", "ATT Education and training / Primary source"
            if sender in policy["designated_education_sources"]:
                return "listed-equivalent-class", "ATT Education and training / Designated equivalent source"
            if label == "State medical society":
                return "not-on-accepted-list", "ATT Education and training / closed list"
        elif row["element"] == "affiliation-and-employment":
            if same_organization and label in ("Medical staff office", "Human resources department", "Authorized administrator"):
                return "listed-primary-class", "ATT Affiliations and employment / Primary source"
    # Do not infer employment authority, aliases, source impossibility, or the
    # meaning of free-form explanations. Those routes need explicit review.
    return "needs-source-review", "ATT: no automatic classification; retain and refer to MSP"


def date_window(received: str, first_received: str, cutoff: str, before_decision=False):
    """A date-only check, not a complete verification/readiness conclusion."""
    if not received or not first_received:
        return "unknown-date"
    try:
        received_day, first_day, cutoff_day = map(date.fromisoformat, (received, first_received, cutoff))
    except ValueError as exc:
        raise GroundworkError("review_date", "Evidence window requires valid recorded dates") from exc
    if received_day < first_day:
        return "before-first-receipt"
    if received_day > cutoff_day or (before_decision and received_day == cutoff_day):
        return "after-or-at-decision" if before_decision else "after-export"
    return "within-date-window-only"


def anniversary(day: date, years: int):
    try:
        return day.replace(year=day.year + years)
    except ValueError:
        return None  # No policy supplied for Feb-29 in a non-leap anniversary year.


def peer_checks(row, discipline: str | None, as_of: str, years=2):
    try:
        signed = date.fromisoformat(row["signature_date"]) if row["signature_date"] else None
        last = date.fromisoformat(row["last_worked_together_end"]) if row["last_worked_together_end"] else None
    except ValueError as exc:
        raise GroundworkError("review_date", "Peer reply has an invalid date; no date was inferred") from exc
    cutoff = anniversary(signed, -years) if signed else None
    expiry = anniversary(signed, years) if signed else None
    recency = None if cutoff is None else True if last is None else cutoff <= last <= signed
    return {
        "same_discipline": None if not discipline or not row["referee_specialty_stated"] else row["referee_specialty_stated"] == discipline,
        "box_says_not_related_or_partner": {"Yes": False, "No": True}.get(row["related_or_partner"]),
        "relationship_text_assessment": "not-evaluated",
        "worked_together_recency_from_returned_dates": recency,
        "signature_current_at_export_only": None if expiry is None else signed <= date.fromisoformat(as_of) <= expiry,
        "signature_second_anniversary": expiry.isoformat() if expiry else None,
        "qualification_conclusion": "not-evaluated",
        "limits": "Returned fields checked individually; no reference count, element state, presentation date or competency judgment",
        "rules": ["P §3 Check 4: eligibility arithmetic and currency"],
    }


def metadata(text: str):
    fields = {}
    for key, value in re.findall(r"^\*\*([^*\r\n]+):\*\*[ \t]*([^\r\n]*)", text, re.MULTILINE):
        if key in fields:
            raise GroundworkError("review_document", "Repeated document metadata; no value was selected")
        fields[key] = value.strip()
    return fields


def authority_checks(fields: dict, policy: dict):
    required = ("Decision ID", "Body", "Signatory", "Role", "Application", "Revision", "Decision date", "Outcome")
    if any(not fields.get(key) for key in required):
        raise GroundworkError("review_document", "Decision lacks required metadata for authority checks")
    day = fields["Decision date"]
    try:
        date.fromisoformat(day)
    except ValueError as exc:
        raise GroundworkError("review_date", "Decision date is invalid") from exc
    body = fields["Body"]
    allowed = fields["Outcome"] in policy["body_outcomes"].get(body, [])
    role = any(r["body"] == body and r["role"] == fields["Role"] and r["name"] == fields["Signatory"]
               and r["from"] <= day <= r["to"] and (r["designation_from"] is None or r["designation_from"] <= day)
               for r in policy["roles"])
    return {
        "body_may_record_outcome": allowed, "signatory_role_on_recorded_date": role,
        "first_failed_authority_check": "body-authority" if not allowed else "signatory-role" if not role else None,
        "final_admission": "not-evaluated",
        "remaining_checks": ["applicant/revision against a presentable packet", "prior packet readiness", "outcome/reason", "supersession"],
        "rules": ["AUTH Who may record what", "AUTH Individual authority and designation", "P §9 first two admission conditions"],
    }


def review(store: Store, state_sha: str, policy_root: Path, policy_sha: str):
    history = store.at(state_sha)  # Deliberately does not inspect a newer HEAD.
    manifest = history["state"]["manifest"]
    policy = load_policy(policy_root, policy_sha, manifest["as_of"])
    tables, documents = read_rows(store, history)
    applications = latest_applications(tables["applications.csv"])
    entries = indexed(tables["declared-history.csv"], "application_id", "revision", "entry_id")
    declarations = indexed(tables["declared-credentials.csv"], "application_id", "revision", "declaration_id")
    source_results, peers, decisions = [], [], []
    for filename, certification in (("verification-replies.csv", False), ("certification-replies.csv", True)):
        for occurrence in tables[filename]:
            row = occurrence["row"]
            app = applications.get(row["application_id"])
            revision = app["row"]["revision"] if app else None
            key = (row["application_id"], revision, row["declaration_id"] if certification else row["entry_id"])
            contexts = (declarations if certification else entries).get(key, [])
            context = contexts[0] if len(contexts) == 1 else None
            classification, rule = source_class(row, context["row"] if context else None, policy, certification)
            anchor, anchor_check = first_receipt_context(tables["applications.csv"], row["application_id"])
            source_results.append({"reply_id": row["reply_id"], "application_id": row["application_id"],
                "recorded_revision_context": revision, "source": occurrence["source"],
                "declared_context_source": context["source"] if context else None,
                "recorded_received_from": row["received_from"], "source_class_check": classification,
                "source_class_rule": rule, "original_outcome": row.get("outcome", row.get("certification_status")),
                "recorded_notes": row.get("notes", ""),
                "received_date": row["received_date"],
                "first_receipt_anchor_check": anchor_check,
                "date_window_as_of_export_only": date_window(row["received_date"], anchor, manifest["as_of"]),
                "date_window_rule": "P §8: first receipt anchor; E export-date clock",
                "reuse_after_revision_changes": "not-evaluated", "verification_conclusion": "not-evaluated"})
    for occurrence in tables["peer-reference-replies.csv"]:
        row = occurrence["row"]
        app = applications.get(row["application_id"])
        peers.append({"reply_id": row["reply_id"], "application_id": row["application_id"], "referee_id": row["referee_id"],
                      "recorded_revision_context": app["row"]["revision"] if app else None,
                      "source": occurrence["source"], "application_source": app["source"] if app else None,
                      "recorded_fields": row,
                      "recorded_signature_date": row["signature_date"],
                      **peer_checks(row, app["row"]["discipline"] if app else None, manifest["as_of"], policy["peer_years"])})
    for document in documents:
        if not document["source"]["path"].startswith("decisions/"):
            continue
        fields = metadata(document["text"])
        decisions.append({"decision_id": fields.get("Decision ID"), "source": document["source"],
                          "recorded_fields": fields, **authority_checks(fields, policy)})
    return {"format": "credentialing-evidence-review/1", "scope": "independent-record-checks-only",
            "state_sha256": state_sha, "batch": manifest["batch"], "as_of": manifest["as_of"],
            "policy_sha256": policy_sha, "policy_sources": policy["sources"],
            "business_blockers": ["G1", "G2"], "assessed_snapshot_written": False,
            "not_evaluated": ["completeness", "CV reconciliation", "packet readiness", "verification element states",
                              "decision admission", "activation", "human judgments", "business action queue"],
            "source_reply_checks": source_results, "peer_field_checks": peers, "decision_authority_checks": decisions,
            "summary": {"source_reply_classes": dict(sorted(Counter(r["source_class_check"] for r in source_results).items())),
                        "peer_replies_checked": len(peers), "decision_records_checked": len(decisions)}}
