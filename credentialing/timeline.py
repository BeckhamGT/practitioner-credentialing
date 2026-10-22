"""Chronological evidence review. No completeness, readiness or positive admission."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

from .review import (authority_checks, first_receipt_context, indexed, latest_applications,
                     load_policy, metadata, read_rows)
from .validation import (DAY, SHA, GroundworkError, confined_file, digest, read_json,
                         schema_validate)


CONTRACT_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["format", "policy_directory", "policy_sha256", "export_guide",
                 "attempt_spacing_days", "peer_overdue_offset_days"],
    "properties": {
        "format": {"const": "credentialing-continuation-rules/1"},
        "policy_directory": {"type": "string", "minLength": 1}, "policy_sha256": SHA,
        "export_guide": {"type": "object", "additionalProperties": False,
                         "required": ["path", "sha256", "version", "effective_from", "url"],
                         "properties": {"path": {"type": "string"}, "sha256": SHA,
                                        "version": {"type": "string"}, "effective_from": DAY,
                                        "url": {"type": "string", "pattern": "^https://"}}},
        "attempt_spacing_days": {"const": 21}, "peer_overdue_offset_days": {"const": 64},
    },
}


def load_contract(path: Path, sha: str, as_of: str):
    if path.is_symlink() or path.parent.is_symlink():
        raise GroundworkError("unsafe_path", "Rules cannot be symlinked")
    root = path.parent.resolve(strict=True)
    raw = confined_file(root, path.name).read_bytes()
    if digest(raw) != sha:
        raise GroundworkError("policy_hash", "Continuation contract differs from pinned hash")
    contract = read_json(raw)
    schema_validate(contract, CONTRACT_SCHEMA)
    source = contract["export_guide"]
    if source["effective_from"] > as_of:
        raise GroundworkError("future_policy", "Export convention is not effective at this clock")
    if digest(confined_file(root, source["path"]).read_bytes()) != source["sha256"]:
        raise GroundworkError("policy_hash", "Export convention bytes differ from pinned hash")
    # Validate the policy directory as a relative confined path via its rules file.
    file = confined_file(root, contract["policy_directory"] + "/rules.json")
    policy = load_policy(file.parent, contract["policy_sha256"], as_of)
    return contract, policy


RESTATED = {
    "declared-history.csv": "entry_id", "declared-credentials.csv": "declaration_id",
    "application-disclosures.csv": "question_code", "privilege-requests.csv": "privilege_code",
}


def differences(before: dict, after: dict, ignored=()):
    return {key: {"before": before.get(key), "after": after.get(key)}
            for key in sorted(before.keys() | after.keys())
            if key not in ignored and before.get(key) != after.get(key)}


def revision_history(tables):
    groups = defaultdict(list)
    for o in tables["applications.csv"]:
        groups[o["row"]["application_id"]].append(o)
    restated = {name: indexed(tables[name], "application_id", "revision") for name in RESTATED}
    result = []
    for app, versions in sorted(groups.items()):
        # Reuse structural identity validation, including ambiguous latest rows.
        latest_applications(versions)
        seen = set()
        previous = None
        prior_revision = 0
        ordered = sorted(versions, key=lambda o: (o["source"]["batch"], o["row"]["received_date"],
                                                  o["source"]["csv_row"]))
        for o in ordered:
            row = o["row"]
            rev = int(row["revision"])
            if rev in seen or rev <= prior_revision:
                raise GroundworkError("review_identity", "Revision history repeats or regresses")
            seen.add(rev)
            item = {"revision": rev, "recorded_fields": row, "source": o["source"],
                    "previous_revision": int(previous["row"]["revision"]) if previous else None,
                    "application_field_changes": differences(previous["row"], row, ("revision",)) if previous else {},
                    "restated_comparisons": {}}
            for name, identity in RESTATED.items():
                def version_map(revision):
                    found = {}
                    for v in restated[name].get((app, revision), []):
                        key = v["row"][identity]
                        if not key or key in found:
                            raise GroundworkError("review_identity", "Ambiguous restated-row identity")
                        found[key] = v
                    return found
                current = version_map(row["revision"])
                old = version_map(previous["row"]["revision"]) if previous else {}
                item["restated_comparisons"][name] = {
                    "identity_column": identity,
                    "added": [{"id": k, **current[k]} for k in sorted(current.keys() - old.keys())],
                    "removed": [{"id": k, **old[k]} for k in sorted(old.keys() - current.keys())],
                    "changed": [{"id": k, "before_source": old[k]["source"], "after_source": current[k]["source"],
                                 "fields": differences(old[k]["row"], current[k]["row"], ("revision",))}
                                for k in sorted(current.keys() & old.keys())
                                if differences(old[k]["row"], current[k]["row"], ("revision",))],
                    "unchanged_ids": [k for k in sorted(current.keys() & old.keys())
                                      if not differences(old[k]["row"], current[k]["row"], ("revision",))],
                }
            item["evidence_reuse_conclusion"] = "not-evaluated"
            item["CV_reconciliation"] = "not-evaluated:G2"
            previous, prior_revision = o, rev
            result.append({"application_id": app, **item})
    return result


def request_history(tables, as_of, contract):
    groups = indexed(tables["verification-attempts.csv"], "application_id", "element", "subject_ref")
    replies = defaultdict(list)
    for name, identity, element in [("verification-replies.csv", "entry_id", None),
                                    ("certification-replies.csv", "declaration_id", "board-certification"),
                                    ("peer-reference-replies.csv", "referee_id", "peer-reference")]:
        for o in tables[name]:
            row = o["row"]
            replies[(row["application_id"], element or row["element"], row[identity])].append(o)
    referees = indexed(tables["peer-referees.csv"], "application_id", "referee_id")
    result = []
    for (app, element, subject), occurrences in sorted(groups.items()):
        ordered = sorted(occurrences, key=lambda o: (o["row"]["attempt_date"], o["source"]["batch"], o["source"]["csv_row"]))
        dates = [date.fromisoformat(o["row"]["attempt_date"]) if o["row"]["attempt_date"] else None for o in ordered]
        observed = replies.get((app, element, subject), [])
        request = {"application_id": app, "element": element, "subject_ref": subject,
                   "attempts": occurrences, "recorded_attempt_count": len(occurrences),
                   "attempt_intervals_days": [(b - a).days if a and b else None for a, b in zip(dates, dates[1:])],
                   "observed_reply_occurrences": observed,
                   "reply_observed": bool(observed), "reply_qualifies": "not-evaluated",
                   "request_satisfied": "not-evaluated", "no_response_is_verification": False}
        if element == "peer-reference":
            anchors = {o["row"]["first_request_date"] for o in referees.get((app, subject), [])}
            anchor = next(iter(anchors)) if len(anchors) == 1 and "" not in anchors else None
            # A first-request/attempt disagreement is not silently repaired.
            if anchor and dates and dates[0] and anchor != dates[0].isoformat():
                anchor = None
            request["peer_first_request_date"] = anchor
            request["peer_first_request_sources"] = referees.get((app, subject), [])
            request["peer_scheduled_dates"] = (
                [(date.fromisoformat(anchor) + timedelta(days=n * contract["attempt_spacing_days"])).isoformat()
                 for n in range(3)] if anchor else None)
            overdue = date.fromisoformat(anchor) + timedelta(days=contract["peer_overdue_offset_days"]) if anchor else None
            request["peer_day64_date"] = overdue.isoformat() if overdue else None
            request["no_returned_row_at_day64"] = as_of >= overdue.isoformat() and not observed if overdue else None
            request["limits"] = "Schedule arithmetic only; no qualifying-reference count, notice sent, fourth reminder, element hold or closure inferred"
        result.append(request)
    return result


def decision_history(tables, documents, policy):
    index = indexed(tables["correspondence.csv"], "application_id")
    apps = indexed(tables["applications.csv"], "application_id")
    result = []
    ids = set()
    for document in documents:
        if not document["source"]["path"].startswith("decisions/"):
            continue
        fields = metadata(document["text"])
        checks = authority_checks(fields, policy)
        identifier = fields["Decision ID"]
        if identifier in ids:
            raise GroundworkError("review_identity", "Duplicate decision identifier; preserve source occurrences and investigate")
        ids.add(identifier)
        receipt = [o for o in index.get((fields["Application"],), [])
                   if o["row"]["document_path"] == document["source"]["path"]
                   and o["source"]["batch"] == document["source"]["batch"]]
        if len(receipt) != 1:
            raise GroundworkError("document_index", "Decision lacks a unique matching correspondence entry")
        known = [o for o in apps.get((fields["Application"],), [])
                 if o["source"]["batch"] <= document["source"]["batch"]
                 and o["row"]["received_date"] and o["row"]["received_date"] <= fields["Decision date"]]
        at_decision = latest_applications(known).get(fields["Application"]) if known else None
        matches = fields["Revision"] == at_decision["row"]["revision"] if at_decision else None
        failed = checks["first_failed_authority_check"]
        if failed is None and matches is False:
            failed = "applicant/revision"
        result.append({"decision_id": identifier, "source": document["source"],
                       "document_sha256": digest(document["text"].encode()), "recorded_fields": fields,
                       "receipt": receipt[0], "authority_checks": checks,
                       "recorded_revision_at_decision_date": at_decision["row"]["revision"] if at_decision else None,
                       "revision_source": at_decision["source"] if at_decision else None,
                       "first_failed_independent_condition": failed,
                       "admitted": False if failed else None,
                       "reason": failed if failed else "Prior presentable packet and packet-revision match unproved: G1/G2",
                       "not_evaluated": ["packet identity/presentability before decision", "outcome/reason", "supersession"],
                       "activation": "not-evaluated"})
    # Receipt date and source row preserve the supplied received ordering, not filename order.
    return sorted(result, key=lambda d: (d["source"]["batch"], d["receipt"]["row"]["date"], d["receipt"]["source"]["csv_row"]))


def timeline(store, state_sha, rules_path, rules_sha):
    history = store.at(state_sha)
    manifest = history["state"]["manifest"]
    contract, policy = load_contract(rules_path, rules_sha, manifest["as_of"])
    tables, documents = read_rows(store, history)
    versions = revision_history(tables)
    requests = request_history(tables, manifest["as_of"], contract)
    decisions = decision_history(tables, documents, policy)
    anchors = [{"application_id": app, "first_received_date": first_receipt_context(tables["applications.csv"], app)[0],
                "anchor_check": first_receipt_context(tables["applications.csv"], app)[1]}
               for app in sorted(latest_applications(tables["applications.csv"]))]
    return {"format": "credentialing-evidence-timeline/1", "scope": "recorded-evidence-only",
            "state_sha256": state_sha, "batch": manifest["batch"], "as_of": manifest["as_of"],
            "predecessor_state_sha256": history["state"]["previous_state_sha256"],
            "rules_sha256": rules_sha, "rule_sources": {**policy["sources"], "E": contract["export_guide"]},
            "assessed_snapshot_written": False, "business_dependencies": ["G1", "G2"],
            "not_evaluated": ["application completeness", "CV reconciliation", "verification reuse",
                              "packet readiness", "positive decision admission", "activation", "business action queue"],
            "first_receipt_anchors": anchors, "application_revisions": versions,
            "request_history": requests, "decision_register": decisions,
            "document_register": [{"source": d["source"], "metadata": metadata(d["text"])} for d in documents],
            "review_tasks": [{"owner": "Medical Services Professional", "due": None,
                              "item": "Review independently refused decision " + d["decision_id"],
                              "decision_source": d["source"]} for d in decisions if d["admitted"] is False],
            "summary": {"applications": len(anchors), "revision_occurrences": len(versions),
                        "attempt_occurrences": sum(r["recorded_attempt_count"] for r in requests),
                        "request_subjects": len(requests), "decision_occurrences": len(decisions),
                        "independent_decision_refusals": dict(sorted(Counter(d["first_failed_independent_condition"]
                                                                             for d in decisions if d["admitted"] is False).items()))}}
