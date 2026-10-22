"""Rule kernels tested on synthetic fixtures only; not wired to supplied-case CLI.

Inputs to these functions are already established facts, not guesses inferred
from CSV receipt fields. None of these helpers supplies a completeness screen,
clinical disposition, CV comparison or packet evidence for actual applicants.
"""

from datetime import date, timedelta
import re

from .review import anniversary, authority_checks
from .validation import GroundworkError


ELEMENTS = {"licensure", "experience", "gaps", "education", "certification", "references"}
ELEMENT_STATES = {"resolved", "finding", "outstanding", "discrepancy", "return-incomplete",
                  "routed-to-clinical-director", "eligibility-question"}


def packet(evidence):
    """P §8: resolved means nothing owed, including properly disposed findings."""
    required = {"application_id", "revision", "complete", "cv_reconciled", "elements",
                "usable_verifications", "open_discrepancy", "last_needed_reply_date"}
    if not required <= evidence.keys() or set(evidence["elements"]) != ELEMENTS:
        raise GroundworkError("conditional_input", "Explicit evidence for all packet dependencies is required")
    for name in ("complete", "cv_reconciled", "usable_verifications", "open_discrepancy"):
        if evidence[name] is not None and type(evidence[name]) is not bool:
            raise GroundworkError("conditional_input", "Packet facts must be booleans or unknown")
    checks = {"completeness": evidence["complete"], "CV reconciliation": evidence["cv_reconciled"],
              "verification usability": evidence["usable_verifications"],
              "no open discrepancy": None if evidence["open_discrepancy"] is None else not evidence["open_discrepancy"]}
    for name, element in evidence["elements"].items():
        if set(element) != {"state", "nothing_owed"} or element["state"] not in ELEMENT_STATES:
            raise GroundworkError("conditional_input", "Element resolution facts must be explicit")
        if element["nothing_owed"] is not None and type(element["nothing_owed"]) is not bool:
            raise GroundworkError("conditional_input", "Element facts must be booleans or unknown")
        checks[name] = element["nothing_owed"]
        if element["state"] not in ("resolved", "finding"):
            checks[name] = False if element["nothing_owed"] is not None else None
    if any(value is not None and type(value) is not bool for value in checks.values()):
        raise GroundworkError("conditional_input", "Expected explicit boolean facts or unknown")
    missing = [name for name, value in checks.items() if value is None]
    ready = False if any(value is False for value in checks.values()) else None if missing else True
    if ready and not evidence["last_needed_reply_date"]:
        missing.append("last needed reply date")
        ready = None
    if evidence["last_needed_reply_date"]:
        date.fromisoformat(evidence["last_needed_reply_date"])
    return {"application_id": evidence["application_id"], "revision": evidence["revision"],
            "presentable": ready, "date": evidence["last_needed_reply_date"] if ready else None,
            "unevaluated_dependencies": missing,
            "failed_checks": [name for name, value in checks.items() if value is False],
            "retained_element_states": {name: element["state"] for name, element in evidence["elements"].items()}}


def decision(fields, policy, recorded_revision, packet_evidence, prior):
    """P §9: stop at the first failed/unknown condition; no outcome rewriting."""
    authority = authority_checks(fields, policy)
    failure = authority["first_failed_authority_check"]
    if failure:
        return {"admitted": False, "reason": failure}
    if recorded_revision is None:
        return {"admitted": None, "reason": "applicant/revision evidence unknown"}
    if fields["Revision"] != str(recorded_revision):
        return {"admitted": False, "reason": "applicant/revision"}
    if packet_evidence is None:
        return {"admitted": None, "reason": "packet identity and prior presentability unknown"}
    if (fields["Application"], fields["Revision"]) != (packet_evidence["application_id"], str(packet_evidence["revision"])):
        return {"admitted": False, "reason": "applicant/revision"}
    if packet_evidence["presentable"] is None:
        return {"admitted": None, "reason": "prior presentability unknown"}
    if (not packet_evidence["presentable"] or not packet_evidence["date"]
            or packet_evidence["date"] >= fields["Decision date"]):
        return {"admitted": False, "reason": "prior presentable packet"}
    if fields["Outcome"] not in ("approved", "recommended") and not fields.get("Reason", "").strip():
        return {"admitted": False, "reason": "outcome/reason"}
    if fields["Body"] == "Governing Body":
        earlier = [p for p in prior if p["fields"]["Body"] == fields["Body"]
                   and p["fields"]["Application"] == fields["Application"]
                   and p["fields"]["Revision"] == fields["Revision"]]
        if any(p["result"]["admitted"] is None for p in earlier):
            return {"admitted": None, "reason": "earlier decision admission unknown"}
        admitted = [p for p in earlier if p["result"]["admitted"] is True]
        if admitted and fields.get("Supersedes") != admitted[-1]["fields"]["Decision ID"]:
            return {"admitted": False, "reason": "supersession"}
        if fields.get("Supersedes") and (not admitted or fields["Supersedes"] != admitted[-1]["fields"]["Decision ID"]):
            return {"admitted": False, "reason": "supersession"}
    return {"admitted": True, "reason": None}


def activation(fields, admission, revision, as_of, published_codes):
    """P §§3/10: only exact grants from an admitted, current-revision GB approval."""
    if admission["admitted"] is None:
        return {"evaluated": False, "activation": None, "dependency": "decision admission unknown"}
    if (admission["admitted"] is not True or fields["Body"] != "Governing Body"
            or fields["Outcome"] not in ("approved", "approved-with-conditions")
            or fields["Revision"] != str(revision)):
        return {"evaluated": True, "activation": None}
    # Actual office records separate multiple grant codes with semicolons.
    grants = [value.strip() for value in re.split(r"[;,]", fields["Privileges"]) if value.strip()]
    if not grants or len(set(grants)) != len(grants) or not set(grants) <= set(published_codes):
        raise GroundworkError("conditional_input", "Grant codes must be distinct published groups")
    start = date.fromisoformat(fields.get("Effective date") or fields["Decision date"])
    if start < date.fromisoformat(fields["Decision date"]):
        raise GroundworkError("conditional_input", "Effective date precedes approval; source clarification needed")
    next_year = anniversary(start, 1)
    if next_year is None:
        return {"evaluated": False, "activation": None, "dependency": "leap-day cycle convention unspecified"}
    end = next_year - timedelta(days=1)
    return {"evaluated": True, "activation": {"active_at_export": start <= date.fromisoformat(as_of) <= end,
            "effective_date": start.isoformat(), "cycle_end": end.isoformat(), "privileges": grants}}


def conditions(owed, satisfaction_records, as_of):
    """P §10: preserve conditions; satisfaction must name the particular condition."""
    result = []
    for condition in owed:
        records = [r for r in satisfaction_records if r["condition"] == condition["condition"] and r["date"] <= as_of]
        satisfied = bool(records)
        finding = not satisfied and as_of >= condition["due"]
        result.append({**condition, "satisfied": satisfied, "satisfaction_records": records,
                       "finding": finding, "owner": "Clinical Director" if finding else "Medical Services Professional",
                       "blocks_activation": False})
    return result


def peer_extra_request(two_qualifying_current, presented, replied):
    """P §3 Check 4: outstanding extra request never counts as a reference."""
    if any(value is None for value in (two_qualifying_current, presented, replied)):
        return {"counts_as_reference": False, "closure": None, "holds_element": None}
    if replied:
        return {"counts_as_reference": None, "closure": "reply-requires-qualification",
                "holds_element": False if two_qualifying_current else None}
    return {"counts_as_reference": False,
            "closure": "no-longer-needed" if two_qualifying_current and presented and not replied else "not-closed-by-this-rule",
            "holds_element": False if two_qualifying_current else None}
