"""Complete dated workflow; unresolved facts stay local to their dependencies.

Source text and the original evidence store remain immutable. Results distinguish
established rules, missing evidence and source-recorded human observations.
"""

from __future__ import annotations

import copy
import re
from collections import Counter, defaultdict
from datetime import date, timedelta

from .conditional import activation, conditions, decision
from .elements import (completed_months, day, direct_work_assertion, gap_explanations,
                       gap_intervals, load_element_rules, wa_observation)
from .human_review import observations
from .review import (anniversary, authority_checks, date_window, first_receipt_context, indexed,
                     latest_applications, metadata, read_rows, source_class)
from .timeline import differences, request_history, revision_history
from .validation import GroundworkError, digest, json_bytes


ELEMENTS = ("licensure", "experience", "gaps", "education", "certification", "references")
ACCEPTED = {"listed-primary-class", "listed-equivalent-class", "secondary-authorized"}
ROW_DATES = {"applications.csv": "received_date", "verification-replies.csv": "received_date",
             "certification-replies.csv": "received_date", "peer-reference-replies.csv": "received_date",
             "verification-attempts.csv": "attempt_date", "peer-referees.csv": "first_request_date",
             "licence-lookup-wa.csv": "lookup_date", "licence-lookup-other-states.csv": "lookup_date",
             "correspondence.csv": "date"}


def all_known(values):
    values = list(values)
    return False if any(v is False for v in values) else None if any(v is None for v in values) else True


def any_known(values):
    values = list(values)
    return True if any(v is True for v in values) else None if any(v is None for v in values) else False


def action(item, owner="Medical Services Professional", due=None, sources=(), kind="owed", dependency=None):
    return {"item": item, "owner": owner, "due": due, "kind": kind,
            "sources": list(sources), "dependency": dependency, "execution": "recorded-source" if kind == "recorded" else "not-sent-or-performed-by-software"}


def element(state, nothing_owed, detail, sources=()):
    return {"state": state, "nothing_owed": nothing_owed, "detail": detail, "sources": list(sources),
            "basis": "current exported declaration and dated source records; CV comparison is a separate file prerequisite"}


def visible(tables, documents, clock, before_decision=False):
    result = defaultdict(list)
    for name, values in tables.items():
        field = ROW_DATES.get(name)
        for occurrence in values:
            value = occurrence["row"].get(field, "") if field else ""
            strict = before_decision and name in {"verification-replies.csv", "certification-replies.csv", "peer-reference-replies.csv"}
            if value and (value > clock or (strict and value == clock)):
                continue
            result[name].append(occurrence)
    versions = {(o["row"]["application_id"], o["row"]["revision"]) for o in result["applications.csv"]}
    for name in ("declared-history.csv", "declared-credentials.csv", "privilege-requests.csv", "application-disclosures.csv", "peer-referees.csv"):
        result[name] = [o for o in result[name] if (o["row"]["application_id"], o["row"]["revision"]) in versions]
    docs = []
    for document in documents:
        fields = metadata(document["text"])
        stamp = fields.get("Date", fields.get("Decision date"))
        if stamp and stamp <= clock and not (before_decision and stamp == clock):
            docs.append(document)
    return result, docs


def role_equivalent(declared, verified):
    for prefix in ("Degree", "Employment", "Affiliation"):
        if verified.startswith(prefix + " — "):
            verified = verified.split(" — ", 1)[1]
    for prefix in ("Residency", "Fellowship"):
        if verified.startswith(prefix + " — "):
            verified = verified.split(" — ", 1)[1] + " " + prefix
    return declared.casefold() == verified.casefold()


def entry_checks(app, tables, clock, policy, human, strict=False):
    row = app["row"];app_id = row["application_id"]
    current = [o for o in tables["declared-history.csv"] if (o["row"]["application_id"], o["row"]["revision"]) == (app_id, row["revision"])]
    anchor, _ = first_receipt_context(tables["applications.csv"], app_id)
    floor = anniversary(day(anchor), -5) if anchor else None
    checked = []
    for occurrence in current:
        entry = occurrence["row"];replies = []
        for source in tables["verification-replies.csv"]:
            reply = source["row"]
            if (reply["application_id"], reply["entry_id"]) != (app_id, entry["entry_id"]):
                continue
            versions = [a for a in tables["applications.csv"] if a["row"]["application_id"] == app_id and a["row"]["received_date"] <= reply["received_date"] and a["source"]["batch"] <= source["source"]["batch"]]
            revision = max(versions, key=lambda a: int(a["row"]["revision"]))["row"]["revision"] if versions else None
            contexts = [o for o in tables["declared-history.csv"] if (o["row"]["application_id"], o["row"]["revision"], o["row"]["entry_id"]) == (app_id, revision, entry["entry_id"])]
            context = contexts[0]["row"] if len(contexts) == 1 else None
            cls, rule = source_class(reply, context, policy)
            if (context and reply["element"] == "affiliation-and-employment" and reply["received_from"].startswith("Credentials verification organization — ")
                    and reply["attester_organization"] == reply["received_from"].split(" — ",1)[1]
                    and ("Retained by " + context["organization"]) in reply["notes"]
                    and ("acting for " + context["organization"]) in reply["notes"]):
                cls,rule = "listed-equivalent-class","ATT Affiliations/employment designated CVO naming retaining affiliation"
            secondary = human.get("secondary_route_by_entry", {}).get("value", {}).get(entry["entry_id"])
            affiliations = [o["row"] for o in current if o["row"]["entry_type"] in ("employment","affiliation") and o["row"]["from_date"] <= clock]
            recent = max(affiliations,key=lambda r:r["from_date"])["organization"] if affiliations else None
            if (cls not in ACCEPTED and secondary is True and reply["received_from"].startswith("Medical staff office — ")
                    and reply["notes"].strip() and reply["attester_organization"] == recent):
                cls = "secondary-authorized"
            changes = differences(context, entry, ("revision",)) if context else None
            non_dates = {k: v for k, v in (changes or {}).items() if k not in ("from_date", "to_date")}
            equal = reply["verified_from"] == entry["from_date"] and reply["verified_to"] == entry["to_date"] and role_equivalent(entry["role"], reply["verified_credential"])
            window = date_window(reply["received_date"], anchor, clock, strict)
            verified = cls in ACCEPTED and window == "within-date-window-only" and reply["outcome"] in ("confirmed", "confirmed-with-discrepancy")
            matches = verified and equal and not non_dates
            replies.append({"row": reply, "source": source["source"], "class": cls, "rule": rule, "window": window,
                            "changed_since_reply": changes, "current_entry_matches": matches,
                            "entry_fields_match":equal and not non_dates,
                            "discrepancy": verified and (not equal or bool(non_dates)), "verified": verified})
        matched = [r for r in replies if r["current_entry_matches"]]
        undecided = [r for r in replies if r["class"] in ("needs-source-review","needs-link-review") and r["window"]=="within-date-window-only" and r["entry_fields_match"] and r["row"]["outcome"] in ("confirmed","confirmed-with-discrepancy")]
        discrepancy = bool(replies) and not matched and any(r["discrepancy"] for r in replies)
        is_education = entry["entry_type"] in ("medical-school", "residency", "fellowship", "other")
        overlap = (day(entry["to_date"]) or day(clock)) >= floor if floor else None
        needs_experience = not is_education and overlap is not False
        # Earlier suspicious/discrepant entries are not dropped below the floor.
        needs_experience = needs_experience or (not is_education and discrepancy)
        checked.append({"entry": entry, "source": occurrence["source"], "education_required": is_education,
                        "experience_required": needs_experience, "five_year_floor": floor.isoformat() if floor else None,
                        "source_verified_current_entry": True if matched else None if undecided else False, "discrepancy": discrepancy, "replies": replies,
                        "accepted_reply_dates": [r["row"]["received_date"] for r in matched]})
    return checked


def component_elements(entries):
    results, queue = {}, []
    for name, flag in (("education", "education_required"), ("experience", "experience_required")):
        selected = [r for r in entries if r[flag]]
        problems = [r for r in selected if r["source_verified_current_entry"] is not True]
        known_unresolved = any(r["source_verified_current_entry"] is False for r in problems)
        state = "discrepancy" if any(r["discrepancy"] for r in problems) else "outstanding" if known_unresolved else None if problems or (name=="education" and not selected) else "resolved"
        done = False if known_unresolved else None if problems or (name=="education" and not selected) else True
        results[name] = element(state, done, {"entries": selected, "scope": "Each known current entry; accepted source, date window and all changed fields checked"})
        for entry in problems:
            replies = entry["replies"]
            text = ("Review source admissibility / documented secondary-route authority without inferring a refusal" if entry["source_verified_current_entry"] is None else "Resolve declaration/source discrepancy in writing without selecting a value" if entry["discrepancy"] else "Obtain an admissible verification of the current entry")
            queue.append(action(f"{text}: {entry['entry']['entry_id']}", sources=[entry["source"]]))
            if replies and any(r["class"] not in ACCEPTED for r in replies):
                queue.append(action(f"Review rejected source / any documented impossibility route for {entry['entry']['entry_id']}; silence is not impossibility", sources=[r["source"] for r in replies]))
    return results, queue


def human_documents(app, documents, rules, organizations=()):
    app_id = app["row"]["application_id"];result = {"terminal": None, "CD": [], "anomalies": [], "confirmations": []}
    own = [d for d in documents if metadata(d["text"]).get("Application") == app_id and not d["source"]["path"].startswith("decisions/")]
    cd = rules["clinical_director"]
    for doc in own:
        fields = metadata(doc["text"]);text = doc["text"];stamp = fields.get("Date", "")
        actor = fields.get("Recorded by") == cd["recorded_by"] and cd["from"] <= stamp <= cd["to"]
        if actor:
            result["CD"].append(doc)
            if re.search(r"(?<!not )\bDiscontinue the application\b", text):
                result["terminal"] = {"status": "discontinued", "date": stamp, "reason": text, "source": doc["source"]}
        if "I am withdrawing my application" in text and fields.get("From") and fields.get("Applicant"):
            name = app["row"]["last_name"]
            if name in fields["From"] and name in fields["Applicant"]:
                result["terminal"] = {"status": "withdrawn", "date": stamp, "reason": text, "source": doc["source"]}
        if "My answer of No was wrong" in text and "correcting it here in writing" in text:
            result["confirmations"].append(doc)
        for label in ("To", "From"):
            value = fields.get(label, "")
            if value and value.startswith("Dr.") and app["row"]["last_name"] not in value:
                result["anomalies"].append({"kind": "identity-metadata", "field": label, "recorded": value, "source": doc["source"]})
        for cited in re.findall(r"explanation of ([0-9]{4}-[0-9]{2}-[0-9]{2})", text):
            if not any(metadata(d["text"]).get("Date") == cited and "Period explained" in metadata(d["text"]) for d in own):
                result["anomalies"].append({"kind": "referenced-explanation-not-in-evidence", "date": cited, "source": doc["source"], "effect": "Preserve identified CD disposition; provenance clarification remains owed"})
        employer = re.search(r"started at (.+?) at the beginning", text)
        if employer and employer[1] not in organizations:
            result["anomalies"].append({"kind": "explanation-employer-needs-reconciliation", "employer_in_text": employer[1], "source": doc["source"], "effect": "Compare with current declared employer; do not adopt a correction"})
    return own, result


def gap_element(history, documents, human, as_of, rules):
    result = gap_explanations(gap_intervals(history, as_of), documents, rules["long_gap_days"])
    unexplained = [g for g in result["gaps"] if not g["written_explanation_observed"]]
    pending = []
    for gap in result["gaps"]:
        dispositions = [d for d in human["CD"] if gap["from"] in d["text"] and gap["to"] in d["text"] and "explanation is sufficient" in d["text"]]
        gap["recorded_dispositions"] = [d["source"] for d in dispositions]
        if gap["requires_clinical_director"] and not dispositions:
            pending.append(gap)
    state = "return-incomplete" if unexplained else "routed-to-clinical-director" if pending else "resolved" if result["evaluated"] else "outstanding"
    queue = [action(f"Obtain written explanation covering {g['from']}–{g['to']}; record return as incomplete under P §1", sources=g["explanations_covering_whole_interval"]) for g in unexplained]
    queue += [action(f"Record disposition on {g['days']}-day gap {g['from']}–{g['to']}", "Clinical Director") for g in pending]
    return element(state, result["evaluated"] and not unexplained and not pending, result), queue


def licence_element(app, tables, declarations, clock, documents, human):
    wa = wa_observation(app, tables, declarations, clock);queue = [];issues = [];owed = [];unknown = []
    restriction = []
    board_docs = [d for d in documents if metadata(d["text"]).get("From") == "Washington State Department of Health"]
    number = wa.get("latest_observation", {}).get("row", {}).get("credentialnumber") if wa.get("latest_observation") else None
    board_docs = [d for d in board_docs if number and number in d["text"]]
    if wa.get("latest_observation") and re.search(r"probation|suspend|restrict|monitor|limitation|surrender",wa["latest_observation"]["row"]["status"],re.I):
        restriction.append(wa["latest_observation"]["source"])
    for doc in board_docs:
        if number and number in doc["text"] and re.search(r"(?:practises under|monitoring programme|agreement .*?remains in force)", doc["text"], re.I):
            restriction.append(doc["source"])
    if wa.get("matched") is False:
        owed.append("Washington credential absent under the explicit export missing-row convention")
    elif wa.get("matched") is None:
        owed.append("Washington identity join needs review")
    elif wa["active_status_on_observation"] is False or wa["unexpired_at_export_from_recorded_expiry"] is False:
        owed.append("Washington licence not current/active at this clock; reverify")
    elif wa["unexpired_at_export_from_recorded_expiry"] is None:
        unknown.append("Washington expiry is not represented; review original board evidence")
    if wa.get("board_reply_review_needed") and not board_docs:
        owed.append("Read issuing board's actual action reply; actiontaken alone is not a restriction")
    others = []
    for d in declarations:
        r = d["row"]
        if r["credential_class"] != "licence" or r["jurisdiction_or_board"] == "WA":
            continue
        matches = [o for o in tables["licence-lookup-other-states.csv"] if o["row"]["board_state"] == r["jurisdiction_or_board"] and o["row"]["licence_number"] == r["number_declared"]]
        accepted = [o for o in matches if o["row"]["verified_by"] == r["issuer"] + " online verification"]
        others.append({"declaration": d, "observations": matches, "verified": bool(accepted)})
        if not accepted:owed.append("Verify declared licence " + r["declaration_id"])
        for o in accepted:
            if o["row"]["disciplinary_action"] == "":
                unknown.append("Review missing other-state action field for " + r["declaration_id"])
            elif o["row"]["disciplinary_action"] not in ("No", "None reported"):
                issues.append(o["source"])
    disposition = [d for d in human["CD"] if "Licensure finding" in d["text"] and "Present the file" in d["text"]]
    if restriction and not disposition:
        owed.append("Clinical Director disposition on the retained licence restriction")
        queue.append(action("Record disposition on licensure finding with board reply", "Clinical Director", sources=restriction))
    for text in owed:
        if not text.startswith("Clinical Director"):
            queue.append(action(text))
    for text in unknown:queue.append(action(text))
    if issues and not disposition:
        owed.append("Disposition on another state's action is owed");queue.append(action("Record disposition on other-state licence action", "Clinical Director", sources=issues))
    state = "finding" if restriction or issues else "outstanding" if owed else None if unknown else "resolved"
    return element(state, False if owed else None if unknown else True, {"Washington": wa, "other_states": others, "restriction_sources": restriction,
                                   "CD_dispositions": [d["source"] for d in disposition], "remaining": owed,
                                   "clean_basis": "Board status, expiry and action record together; actiontaken alone is never used"}), queue


def peer_element(app, tables, clock, policy, strict=False, presentation=None):
    app_id = app["row"]["application_id"];anchor, _ = first_receipt_context(tables["applications.csv"], app_id)
    rows = [];latest = {}
    from .review import peer_checks
    for occurrence in tables["peer-reference-replies.csv"]:
        r = occurrence["row"]
        if r["application_id"] != app_id:continue
        fields = peer_checks(r, app["row"]["discipline"], presentation or clock)
        direct = direct_work_assertion(r["relationship_stated"])
        relationship = fields["box_says_not_related_or_partner"]
        if relationship is True and re.search(r"\b(?:sister|brother|relative|spouse|partner|wife|husband|cousin|mother|father)\b", r["relationship_stated"], re.I):
            relationship = None  # Prose needs review; do not infer an affirmative relationship or a pass.
        eligible = all_known([fields["same_discipline"], relationship, fields["worked_together_recency_from_returned_dates"], direct])
        window = date_window(r["received_date"], anchor, clock, strict)
        qualifies = all_known([eligible, fields["signature_current_at_export_only"], window == "within-date-window-only"])
        value = {"row": r, "source": occurrence["source"], "eligibility": eligible, "current": fields["signature_current_at_export_only"], "qualifies_at_this_clock": qualifies, "window": window, "fields": fields}
        rows.append(value)
        if r["referee_id"] not in latest or r["received_date"] > latest[r["referee_id"]]["row"]["received_date"]:
            latest[r["referee_id"]] = value
    count = sum(r["qualifies_at_this_clock"] is True for r in latest.values())
    unknown = sum(r["qualifies_at_this_clock"] is None for r in latest.values())
    met = True if count >= 2 else None if count + unknown >= 2 else False
    queue = [] if met is True else [action(f"Obtain two qualifying current references; {count} established at {clock}. Retain all ineligible/stale replies")]
    selected = sorted((r for r in latest.values() if r["qualifies_at_this_clock"] is True), key=lambda r:r["row"]["received_date"])[:2]
    return element("resolved" if met else "outstanding", met, {"clock": clock, "currency_clock":presentation or clock, "qualifying_distinct_referees": count, "unknown_qualification": unknown, "replies": rows, "needed_reply_dates": [r["row"]["received_date"] for r in selected]}), queue


def certification_element(app, tables, entries, requests, declarations, clock, rules, policy, human, strict=False):
    app_id = app["row"]["application_id"];anchor, _ = first_receipt_context(tables["applications.csv"], app_id)
    certificates = [];queue = [];missing = [];discrepancies = []
    for d in declarations:
        r = d["row"]
        if r["credential_class"] != "certification":continue
        replies = []
        for o in tables["certification-replies.csv"]:
            v = o["row"]
            if (v["application_id"], v["declaration_id"]) != (app_id, r["declaration_id"]):continue
            cls, cite = source_class(v, r, policy, True)
            usable = cls in ACCEPTED and date_window(v["received_date"], anchor, clock, strict) == "within-date-window-only"
            replies.append({"row": v, "source": o["source"], "usable": usable, "class": cls, "rule": cite})
        usable = [o for o in replies if o["usable"]]
        latest = max(usable, key=lambda o: o["row"]["received_date"]) if usable else None
        if not latest:missing.append(r["declaration_id"])
        elif latest["row"]["certification_status"] == "Inactive" and r["declared_status"] not in ("Inactive", "Lapsed", "Expired"):
            discrepancies.append(r["declaration_id"])
        certificates.append({"declaration": d, "replies": replies, "latest": latest})
    groups = []
    accreditation = human.get("accreditation_by_entry", {}).get("value", {})
    for req in requests:
        code = req["row"]["privilege_code"];criterion = rules["criteria"].get(code)
        if not criterion:
            groups.append({"code": code, "supported": False, "reason": "Code not published"});continue
        cert_flags = [];inactive = False;prohibited = False
        for c in certificates:
            if c["latest"] is None:cert_flags.append(None);continue
            v = c["latest"]["row"]
            matched = any(v["board_code"] == board and specialty is not None and v["certificate_specialty"] == specialty for board, specialty in criterion["certifications"])
            if not matched:continue
            active = v["certification_status"] == "Active" and (not v["expiry_date"] or v["expiry_date"] >= clock)
            inactive = inactive or v["certification_status"] == "Inactive" or bool(v["expiry_date"] and v["expiry_date"] < clock)
            eligible = re.search(r"Candidate in good standing; board eligible through ([0-9]{4}-[0-9]{2}-[0-9]{2})", v["notes"])
            permitted = bool(eligible and code in rules["board_eligible_groups"] and eligible[1] > clock)
            prohibited = prohibited or bool(eligible and (code not in rules["board_eligible_groups"] or eligible[1] <= clock))
            cert_flags.append(active or permitted)
        cert = any_known(cert_flags)
        training = []
        for label, months in criterion["training"]:
            matches = []
            for e in entries:
                for response in e["replies"]:
                    candidate = (response["current_entry_matches"] or (e["source_verified_current_entry"] is None and response["entry_fields_match"]))
                    if candidate and response["row"]["verified_credential"] == label:
                        duration = True if months is None else completed_months(response["row"]["verified_from"], response["row"]["verified_to"], months)
                        acc = accreditation.get(e["entry"]["entry_id"])
                        matches.append({"entry_id": e["entry"]["entry_id"], "source": response["source"], "duration": duration, "accreditation": acc, "meets": all_known([duration, acc,e["source_verified_current_entry"]])})
            training.append({"required_title": label, "minimum_months": months, "observations": matches, "met": any_known(v["meets"] for v in matches)})
        train = (all_known if criterion["training_combination"] == "all" else any_known)(v["met"] for v in training)
        degree_entries = [e for e in entries if e["entry"]["entry_type"] == "medical-school"]
        degree = any_known(all_known([e["source_verified_current_entry"], e["entry"]["role"] in ("Doctor of Medicine", "Doctor of Osteopathic Medicine"), accreditation.get(e["entry"]["entry_id"])]) for e in degree_entries)
        supported = all_known([cert, train, degree])
        if supported is False and (cert is True) != (train is True) and not ((inactive or prohibited) and cert is not True) and code != "PRIV-CARD":
            # Rule 2's "neither" wording does not settle one-component classification.
            supported = None
        groups.append({"code": code, "supporting_certification": cert, "training": training, "training_met": train,
                       "supported": supported, "qualifying_accredited_degree": degree, "inactive_certificate_supports_nothing": inactive,
                       "criteria_version": rules["criteria_version"], "current_experience": "reserved-clinical-leadership"})
    unsupported = [g["code"] for g in groups if g["supported"] is False]
    unknown = [g["code"] for g in groups if g["supported"] is None]
    supported = [g["code"] for g in groups if g["supported"] is True]
    if missing:queue.append(action("Obtain admissible board verification for " + ", ".join(missing)))
    if discrepancies:queue.append(action("Resolve declared versus board certification status in writing: " + ", ".join(discrepancies)))
    if unknown:queue.append(action("Establish missing privilege-support component/accreditation or scoped G6 interpretation: " + ", ".join(unknown)))
    eligibility = bool(groups) and len(unsupported) == len(groups)
    if eligibility:queue.append(action("Record eligibility disposition or offer amendment; no supported requested group", "Clinical Director"))
    state = "discrepancy" if discrepancies else "outstanding" if missing else "eligibility-question" if eligibility else "finding" if unsupported else None if unknown else "resolved"
    done = False if missing or discrepancies or eligibility else None if unknown else True
    return element(state, done, {"certificates": certificates, "groups": groups, "supported": supported, "unsupported": unsupported,
                                "conditional_components": unknown, "verification_complete": not missing,
                                "scope": "No accreditation pass or one-component interpretation invented"}), queue


def intake(app, tables, docs, gaps, requests, entries, human, clock, rules):
    row = app["row"];app_id = row["application_id"]
    own = [d for d in docs if metadata(d["text"]).get("Application") == app_id]
    notices = [d for d in own if "30 calendar days" in d["text"] and ("# Missing items on your application" in d["text"] or "# Application returned as incomplete" in d["text"])]
    release = True if row["release_signed_date"] and row["release_signed_date"] <= clock else False if any("Release, signed and dated" in d["text"] for d in notices) else None
    cv_missing = any("current curriculum vitae" in d["text"] for d in notices) and not row["cv_received_date"]
    cv = human.get("cv_current", {}).get("value", False if cv_missing else None)
    ppq = [o for o in tables["application-disclosures.csv"] if (o["row"]["application_id"], o["row"]["revision"]) == (app_id, row["revision"])]
    named = [o for o in tables["peer-referees.csv"] if o["row"]["application_id"] == app_id and int(o["row"]["revision"]) <= int(row["revision"])]
    history_ok = all(g["written_explanation_observed"] for g in gaps["detail"]["gaps"]) if gaps["detail"]["evaluated"] else None
    screen = {"1_application_signed_and_dated": human.get("application_signature", {}).get("value"),
              "2_release_signed_and_dated": release,
              "3_specific_published_privilege_request": bool(requests) and all(o["row"]["privilege_code"] in rules["criteria"] for o in requests),
              "4_current_CV": cv,
              "5_professional_questions": set(o["row"]["question_code"] for o in ppq) == set(rules["practice_question_codes"]) and all(o["row"]["answer"] in ("Yes", "No") and (o["row"]["answer"] != "Yes" or bool(o["row"]["applicant_comment"].strip())) for o in ppq),
              "6_explained_continuous_declared_history": history_ok,
              "7_two_named_referees": len({o["row"]["referee_id"] for o in named}) >= 2,
              "8_affiliation_employer_contacts": all(e["entry"]["contact_name"] and e["entry"]["contact_email"] for e in entries if not e["education_required"]),
              "9_all_credentials_declared": human.get("all_credentials_declared", {}).get("value")}
    clocks = []
    versions = [o["row"] for o in tables["applications.csv"] if o["row"]["application_id"] == app_id]
    for doc in notices:
        stamp = metadata(doc["text"])["Date"];due = (day(stamp) + timedelta(days=30)).isoformat()
        literal = re.search(r"that is by ([0-9]{4}-[0-9]{2}-[0-9]{2})", doc["text"])
        if literal and literal[1] != due:
            raise GroundworkError("notice_clock", "Written due date conflicts with thirty-day rule; preserve and review")
        needed = []
        if "Release, signed and dated" in doc["text"]:needed.append("release_signed_date")
        if "current curriculum vitae" in doc["text"]:needed.append("cv_received_date")
        cures = []
        for field in needed:
            dates = [v[field] for v in versions if v[field] and v[field] <= clock]
            cures.append(min(dates) if dates else None)
        if "# Application returned as incomplete" in doc["text"]:
            relevant = [g for g in gaps["detail"]["gaps"] if g["from"] in doc["text"] and g["to"] in doc["text"]]
            explanation_dates = [e["metadata"]["Date"] for g in relevant for e in g["explanations_covering_whole_interval"]]
            cures.append(min(explanation_dates) if explanation_dates else None)
        fulfilled = max(cures) if cures and all(cures) else None
        late = clock > due and (fulfilled is None or fulfilled > due)
        clocks.append({"written_date": stamp, "due": due, "cure_dates": cures, "requested_items_received": fulfilled,
                       "expired_with_missing_requested_item": late, "deadline_inclusive": True, "resets_on_revision": False,
                       "source": doc["source"], "scope": "Recorded requested items; unavailable G1/G2 export evidence never creates a notice or a clock"})
    complete = all_known(screen.values())
    return {"conditions": screen, "complete": complete,
            "CV_reconciled": human.get("cv_reconciled", {}).get("value"), "human_observations": human,
            "working_referee_addresses": "outside export; neither met nor failed, E What I do not export",
            "clocks": clocks, "release_permission":release, "verification_request_permitted": all_known([release,complete]),
            "receipt_fields_are_not_signature_or_CV_content": True}


def high_risk(app, tables, own, human):
    row = app["row"]
    yes = [o for o in tables["application-disclosures.csv"] if (o["row"]["application_id"], o["row"]["revision"]) == (row["application_id"], row["revision"]) and o["row"]["answer"] == "Yes"]
    contradiction = [d for d in own if metadata(d["text"]).get("From") == "Washington State Department of Health" and "monitoring programme" in d["text"]]
    ppq1 = [o for o in tables["application-disclosures.csv"] if (o["row"]["application_id"], o["row"]["revision"], o["row"]["question_code"]) == (row["application_id"], row["revision"], "PPQ-1")]
    requires_confirmation = bool(contradiction and ppq1 and ppq1[0]["row"]["answer"] == "No")
    recorded = [d for d in human["CD"] if "High-risk finding" in d["text"] or "high-risk finding" in d["text"]]
    exists = bool(yes or requires_confirmation)
    owed = exists and (not recorded or (requires_confirmation and not human["confirmations"]))
    queue = []
    if requires_confirmation and not human["confirmations"]:
        queue.append(action("Obtain written confirmation/correction of PPQ-1 contradicted by board evidence", sources=[d["source"] for d in contradiction]))
    if exists and not recorded:queue.append(action("Record high-risk disposition; retain evidence for MEC and GB", "Clinical Director", sources=[o["source"] for o in yes]))
    return {"finding_retained": exists, "yes_rows": yes, "contradicted_no": requires_confirmation,
            "confirmation_sources": [d["source"] for d in human["confirmations"]], "dispositions": [d["source"] for d in recorded], "nothing_owed": not owed}, queue


def evaluate(app, tables, documents, clock, rules, policy, roster_text, strict=False, presentation=None):
    row = app["row"];key = (row["application_id"], row["revision"])
    organizations = [o["row"]["organization"] for o in tables["declared-history.csv"] if (o["row"]["application_id"],o["row"]["revision"])==key]
    own, records = human_documents(app, documents, rules, organizations)
    human = observations(documents, key[0], row["revision"], roster_text)
    cleared = human.get("resolved_source_concerns",{})
    for concern in records["anomalies"]:
        correction = cleared.get("value",{}).get(concern["source"]["sha256"])
        concern["resolved_by"] = {"review":cleared["source"],"correcting_source_sha256":correction} if correction else None
    entries = entry_checks(app, tables, clock, policy, human, strict)
    elems, queue = component_elements(entries)
    requests = [o for o in tables["privilege-requests.csv"] if (o["row"]["application_id"], o["row"]["revision"]) == key]
    declarations = [o for o in tables["declared-credentials.csv"] if (o["row"]["application_id"], o["row"]["revision"]) == key]
    elems["gaps"], extra = gap_element([e["entry"] for e in entries], own, records, clock, rules);queue += extra
    elems["licensure"], extra = licence_element(app, tables, declarations, clock, own, records);queue += extra
    elems["references"], extra = peer_element(app, tables, clock, policy, strict, presentation);queue += extra
    elems["certification"], extra = certification_element(app, tables, entries, requests, declarations, clock, rules, policy, human, strict);queue += extra
    screen = intake(app, tables, documents, elems["gaps"], requests, entries, human, clock, rules)
    for name, value in screen["conditions"].items():
        if value is False:
            queue.append(action("Resolve recorded completeness item: " + name.split('_',1)[1].replace('_',' ') + "; a new written notice is not inferred"))
    for recorded in screen["clocks"]:
        queue.append(action("Written missing-item/return request recorded; original deadline retained", due=recorded["due"], sources=[recorded["source"]], kind="recorded"))
    for document in own:
        fields = metadata(document["text"])
        if fields.get("To"):
            queue.append(action("Recorded correspondence: " + document["text"].splitlines()[0].lstrip('# '), sources=[document["source"]], kind="recorded"))
    risk, extra = high_risk(app, tables, own, records);queue += extra
    for code, description, names in [("G1", "Inspect actual signed/dated application tied to this revision and all-credentials attestation", ("1_application_signed_and_dated", "9_all_credentials_declared")),
                                      ("G2", "Inspect current CV contents/version at intake and reconcile it with application and completed verifications", ("4_current_CV",))]:
        if any(screen["conditions"][n] is None for n in names) or (code == "G2" and screen["CV_reconciled"] is None):
            queue.append(action(description + "; obtain source documents or explicit authorized export representation", dependency=code))
    for anomaly in records["anomalies"]:
        queue.append(action(("Source clarification recorded: " if anomaly["resolved_by"] else "Clarify scoped source anomaly: ") + anomaly["kind"], sources=[anomaly["source"]],kind="recorded" if anomaly["resolved_by"] else "owed"))
    discrepancy = any(e["state"] == "discrepancy" for e in elems.values())
    narrative_review = any(a["kind"] == "explanation-employer-needs-reconciliation" and not a["resolved_by"] for a in records["anomalies"])
    no_discrepancy = False if discrepancy else None if narrative_review else True
    requirements = {"intake_complete": screen["complete"], "CV_reconciled": screen["CV_reconciled"], "no_open_discrepancy": no_discrepancy,
                    "high_risk_disposition": risk["nothing_owed"], **{k: e["nothing_owed"] for k, e in elems.items()}}
    ready = all_known(requirements.values())
    reply_dates = []
    for e in entries:
        if (e["education_required"] or e["experience_required"]) and e["accepted_reply_dates"]:
            reply_dates.append(min(e["accepted_reply_dates"]))
    reply_dates += elems["references"]["detail"]["needed_reply_dates"]
    reply_dates += [c["latest"]["row"]["received_date"] for c in elems["certification"]["detail"]["certificates"] if c["latest"]]
    packet_date = max(reply_dates) if reply_dates else None
    if ready is True and packet_date is None:ready = None
    status = None
    if records["terminal"]:status = records["terminal"]["status"]
    elif any(c["expired_with_missing_requested_item"] for c in screen["clocks"]):status = "ineligible-clock-expired"
    elif elems["gaps"]["state"] == "return-incomplete" and screen["clocks"]:status = "returned-incomplete"
    elif any(not c["requested_items_received"] for c in screen["clocks"]):status = "intake-incomplete"
    elif screen["complete"] is True:status = "packet-presentable" if ready is True else "in-verification"
    if ready is False:
        queue.append(action("Packet cannot be presented: " + ", ".join(k for k,v in requirements.items() if v is False)))
    elif ready is None:
        queue.append(action("Establish unresolved packet prerequisites: " + ", ".join(k for k,v in requirements.items() if v is None)))
    if records["terminal"]:
        queue = [{**q, "kind": "historical-review" if q["dependency"] in ("G1", "G2") else "closed-operational", "execution": "No new requests on ended file; evidence retained"} for q in queue]
        queue.append(action("Terminal reason recorded; file is not appointed", sources=[records["terminal"]["source"]], kind="recorded"))
    return {"application_id": key[0], "revision": int(row["revision"]), "as_of": clock,
            "documents_read":[{"source":d["source"],"text":d["text"]} for d in documents if metadata(d["text"]).get("Application")==key[0]],
            "intake": screen, "elements": elems, "high_risk": risk, "human_records": records,
            "packet": {"application_id": key[0], "revision": int(row["revision"]), "presentable": ready,
                       "date": packet_date if ready is True else None, "requirements": requirements,
                       "established_negative_dependencies": [k for k,v in requirements.items() if v is False],
                       "unknown_dependencies": [k for k,v in requirements.items() if v is None]},
            "status": status, "action_queue": queue, "approval_decision_id": None, "activation": None, "monitored_conditions": []}


def recorded_conditions(text):
    result = []
    if "**Conditions:**" in text:
        section = text.split("**Conditions:**", 1)[1].split("\n## ", 1)[0]
        for line in section.splitlines():
            if not line.startswith("- "):continue
            match = re.fullmatch(r"- (.+?) — due ([0-9]{4}-[0-9]{2}-[0-9]{2})\s*", line)
            if not match:
                result.append({"condition":line[2:].strip(),"due":None,"unparsed_due":True});continue
            day(match[2]);result.append({"condition": match[1], "due": match[2]})
    return result


def finish_case(case, decisions, documents, tables, clock, contract, rules, roster_text):
    app_id = case["application_id"];revision = case["revision"];terminal = case["human_records"]["terminal"]
    own = [d for d in decisions if d["fields"]["Application"] == app_id]
    admitted = [d for d in own if d["result"]["admitted"] is True and d["fields"]["Body"] == "Governing Body" and d["fields"]["Revision"] == str(revision)]
    governing = admitted[-1] if admitted else None
    queue = case["action_queue"]
    for record in own:
        if record["result"]["admitted"] is False:
            queue.append(action(f"Review refused decision {record['fields']['Decision ID']}: {record['result']['reason']}", sources=[record["source"]]))
        elif record["result"]["admitted"] is None:
            awaited = ("; received deferral awaits: " + record["fields"].get("Reason", "")) if record["fields"]["Outcome"]=="deferred-pending-information" else ""
            queue.append(action(f"Complete admission review for {record['fields']['Decision ID']}: {record['result']['reason']}"+awaited, sources=[record["source"]], dependency="decision-prerequisites"))
    if governing:
        fields = governing["fields"];outcome = fields["Outcome"]
        if outcome in ("approved", "approved-with-conditions"):
            case["approval_decision_id"] = fields["Decision ID"]
            grant = activation(fields, governing["result"], revision, clock, rules["criteria"])
            if grant["evaluated"]:
                case["approval_decision_id"] = fields["Decision ID"];case["activation"] = grant["activation"]
                unknown_conditions = outcome=="approved-with-conditions" and (not governing["conditions"] or any(c["due"] is None for c in governing["conditions"]))
                case["condition_details_unresolved"] = unknown_conditions
                if unknown_conditions:queue.append(action("Obtain the exact named conditions and due dates from the admitted approval; activation is not blocked by monitored conditions",sources=[governing["source"]]))
                owed = [copy.deepcopy(c) for c in governing["conditions"] if c["due"] is not None]
                board = case["elements"]["licensure"]["detail"]["Washington"].get("latest_observation")
                if board:
                    expiry = board["row"]["expirationdate"]
                    if grant["activation"]["effective_date"] <= expiry <= grant["activation"]["cycle_end"]:
                        owed.append({"condition": "Re-verify Washington licence " + board["row"]["credentialnumber"] + " before expiry", "due": expiry,
                                     "origin":"licence-expiry", "credential_number":board["row"]["credentialnumber"]})
                for old in case.get("prior_monitored_conditions", []):
                    if old.get("origin") == "licence-expiry" and not any((o["condition"],o["due"]) == (old["condition"],old["due"]) for o in owed):
                        owed.append({k:old[k] for k in ("condition","due","origin","credential_number")})
                satisfied = []
                for doc in documents:
                    m = metadata(doc["text"]);condition = m.get("Condition satisfied")
                    actor = m.get("Recorded by", "")
                    if m.get("Application") != app_id or not condition:continue
                    cd_ok = actor == rules["clinical_director"]["recorded_by"] and rules["clinical_director"]["from"] <= m.get("Date", "") <= rules["clinical_director"]["to"]
                    msp_ok = bool(actor and f"Medical Services Professional\n{actor}\ncontinuing" in roster_text)
                    if "Clinical Director" in condition and not cd_ok:continue
                    if cd_ok or msp_ok:satisfied.append({"condition": condition, "date": m["Date"], "source": doc["source"]})
                tracked = conditions(owed, satisfied, clock)
                for c in tracked:
                    dates = sorted(r["date"] for r in c["satisfaction_records"])
                    events = []
                    if clock >= c["due"] and (not dates or dates[0] > c["due"]):
                        events.append({"date":c["due"],"event":"became-finding","owner":"Clinical Director","notification_sent":False})
                    if dates:events.append({"date":dates[0],"event":"satisfied-by-naming-record"})
                    c["events"] = events
                # Board renewal is a named re-verification of that licence, not satisfaction of unrelated conditions.
                if board:
                    for c in tracked:
                        if (c.get("origin") == "licence-expiry" and board["row"]["credentialnumber"] == c["credential_number"]
                                and board["row"]["expirationdate"] > c["due"] and board["row"]["status"] == "ACTIVE"):
                            c.update(satisfied=True, satisfaction_records=[board["source"]], finding=False)
                            c["events"] = ([{"date":c["due"],"event":"became-finding","owner":"Clinical Director","notification_sent":False}] if board["row"]["lookup_date"] > c["due"] else []) + [{"date":board["row"]["lookup_date"],"event":"satisfied-by-named-licence-reverification"}]
                case["monitored_conditions"] = tracked
                for c in tracked:
                    if not c["satisfied"]:queue.append(action(c["condition"], c["owner"], c["due"], dependency="monitored-condition"))
                case["status"] = "approved-not-yet-effective" if grant["activation"]["effective_date"] > clock else "active-with-conditions" if grant["activation"]["active_at_export"] and any(not c["satisfied"] for c in tracked) else "active" if grant["activation"]["active_at_export"] else None
                if unknown_conditions and grant["activation"]["active_at_export"]:case["status"] = None
            else:queue.append(action("Resolve activation dependency: " + grant["dependency"]))
        elif outcome == "deferred-pending-information":
            case["status"] = "deferred";queue.append(action("Chase exactly the admitted deferral's awaited information: " + fields["Reason"], sources=[governing["source"]]))
        elif outcome == "denied":case["status"] = "denied"
    elif any(d["result"]["admitted"] is False for d in own) and case["status"] not in ("intake-incomplete", "returned-incomplete", "ineligible-clock-expired"):
        case["status"] = "decision-inadmissible"
    if terminal:
        case["status"] = terminal["status"];case["activation"] = None;case["approval_decision_id"] = None
    requests = [r for r in request_history(tables, clock, contract) if r["application_id"] == app_id]
    met = case["elements"]["references"]["nothing_owed"] is True
    presented = bool(any(d["result"]["admitted"] is True for d in own))
    for request in requests:
        peer = request["element"] == "peer-reference"
        request["operationally_closed"] = "terminal-file" if terminal else "no-longer-needed" if peer and met and presented and not request["reply_observed"] else None
        request["counts_as_reference"] = False if not request["reply_observed"] else None
        if not request["reply_observed"] and not request["operationally_closed"]:
            if peer and met:
                queue.append(action("Keep extra unanswered reference request visible until presentation; it does not hold the met element: " + request["subject_ref"]))
            elif peer and request.get("no_returned_row_at_day64"):
                queue.append(action("Ask applicant for an additional referee; original overdue request stays open: " + request["subject_ref"], due=request["peer_day64_date"]))
            elif request["recorded_attempt_count"] < 3:
                dates = [o["row"]["attempt_date"] for o in request["attempts"] if o["row"]["attempt_date"]]
                due = (day(max(dates)) + timedelta(days=contract["attempt_spacing_days"])).isoformat() if dates else None
                queue.append(action("Next required verification attempt (send only with signed release): " + request["subject_ref"], due=due))
            elif not peer:
                queue.append(action("Non-response after three attempts is a red flag; review/chase accepted source, not impossibility: " + request["subject_ref"]))
    for q in queue:
        if terminal and q["kind"] == "owed":q["kind"] = "historical-review";q["execution"] = "Ended file; retain audit work without sending operational requests"
        q["action_id"] = digest(json_bytes({"app": app_id, "revision": revision, "item": q["item"], "owner": q["owner"], "due": q["due"]}))[:20]
    case["action_queue"] = list({q["action_id"]:q for q in queue}.values())
    case["requests"] = requests;case["decisions"] = own
    case["element_result_classes"] = {k:"missing-evidence" if v["nothing_owed"] is None else "established-within-exported-scope" for k,v in case["elements"].items()}
    case.pop("prior_monitored_conditions", None)
    candidate = {"application_id": app_id, "revision": revision, "status": case["status"],
                 "elements": {k: e["state"] for k,e in case["elements"].items()}, "packet_presentable": case["packet"]["presentable"],
                 "decisions": [{"decision_id": d["fields"]["Decision ID"], "admitted": d["result"]["admitted"], "reason": d["result"]["reason"] if d["result"]["admitted"] is False else None} for d in own],
                 "approval_decision_id": case["approval_decision_id"], "activation": case["activation"],
                 "monitored_conditions": [{"condition": c["condition"], "due": c["due"]} for c in case["monitored_conditions"] if not c["satisfied"]],
                 "action_queue": [{k:q[k] for k in ("item", "owner", "due")} for q in case["action_queue"]]}
    conflicts = []
    if candidate["status"] is None:conflicts.append("status: no established existing enum for unresolved intake")
    if candidate["packet_presentable"] is None:conflicts.append("packet_presentable: required boolean is unknown")
    if case.get("condition_details_unresolved"):conflicts.append("monitored_conditions: source lacks exact condition/due details")
    if candidate["approval_decision_id"] is not None and candidate["activation"] is None:conflicts.append("activation: approved cycle cannot yet be represented")
    for name, value in candidate["elements"].items():
        if value is None:conflicts.append("elements/" + name + ": final enum requires missing support evidence")
    for d in candidate["decisions"]:
        if d["admitted"] is None:conflicts.append("decisions/" + d["decision_id"] + "/admitted: ordered admission is unresolved")
    case["schema_application"] = candidate if not conflicts else None;case["schema_conflicts"] = conflicts
    return case


def brief(case):
    return {"revision": case["revision"], "status": case["status"], "complete": case["intake"]["complete"],
            "elements": {k:{"state":v["state"], "nothing_owed":v["nothing_owed"]} for k,v in case["elements"].items()},
            "packet": case["packet"], "terminal": case["human_records"]["terminal"]}


def process(store, state_sha, rule_path, rule_sha, previous=None, previous_sha=None):
    retained = store.at(state_sha);manifest = retained["state"]["manifest"];batch = manifest["batch"];clock = manifest["as_of"]
    if batch == 1 and previous is not None or batch > 1 and (previous is None or previous["batch"] != batch-1 or previous["evidence_state_sha256"] != retained["state"]["previous_state_sha256"]):
        raise GroundworkError("workflow_predecessor", "Exact preceding workflow/evidence state is required; never restart batch three")
    if previous and (previous["rules_sha256"] != rule_sha or digest(json_bytes(previous)) != previous_sha):
        raise GroundworkError("workflow_predecessor", "Prior workflow bytes/rules differ from the pinned predecessor")
    rules, contract, policy = load_element_rules(rule_path, rule_sha, clock)
    policy_root = rule_path.parent / contract["policy_directory"]
    roster = (policy_root / policy["sources"]["AUTH"]["path"]).read_text()
    tables, documents = read_rows(store, retained)
    synthetic = [o["row"]["application_id"].startswith("SYNTH-") for o in tables["applications.csv"]]
    if any(synthetic) and not all(synthetic):raise GroundworkError("mixed_dataset", "Synthetic and supplied applicant inputs cannot share a workflow")
    decisions = copy.deepcopy(previous["decision_history"]) if previous else []
    current_decisions = []
    correspondence = {(o["source"]["batch"],o["row"]["document_path"]):o for o in tables["correspondence.csv"]}
    for doc in documents:
        if doc["source"]["batch"] == batch and doc["source"]["path"].startswith("decisions/"):
            receipt = correspondence[(batch,doc["source"]["path"])];current_decisions.append((receipt["row"]["date"],receipt["source"]["csv_row"],doc))
    for _, _, doc in sorted(current_decisions):
        fields = metadata(doc["text"]);when = fields["Decision date"]
        viewed, docs = visible(tables, documents, when, True)
        app = latest_applications(viewed["applications.csv"]).get(fields["Application"])
        context = evaluate(app, viewed, docs, when, rules, policy, roster, True) if app else None
        packet = copy.deepcopy(context["packet"]) if context else None
        if packet and app["row"]["received_date"] >= when:
            packet["presentable"] = False;packet["date"] = None
        prior = [d for d in decisions if d["fields"]["Application"] == fields["Application"]]
        result = decision(fields, policy, context["revision"] if context else None, packet, prior)
        authority = authority_checks(fields,policy)
        earlier = [d for d in prior if d["fields"]["Body"]==fields["Body"]=="Governing Body" and d["fields"]["Revision"]==fields["Revision"]]
        reason_ok = fields["Outcome"] in ("approved","recommended") or bool(fields.get("Reason","").strip())
        decisions.append({"fields":fields, "result":result, "source":doc["source"], "observed_in_batch":batch,
                          "independent_conditions":{"body":authority["body_may_record_outcome"],"signatory_role":authority["signatory_role_on_recorded_date"],
                              "recorded_revision":fields["Revision"]==str(context["revision"]) if context else None,
                              "prior_presentability":packet["presentable"] if packet else None,"outcome_reason":reason_ok,
                              "earlier_same_body_records":[d["fields"]["Decision ID"] for d in earlier],
                              "literal_supersedes":fields.get("Supersedes") or None,
                              "names_prior_received_record":fields.get("Supersedes","") in [d["fields"]["Decision ID"] for d in earlier],
                              "supersession_applicability_known":not any(d["result"]["admitted"] is None for d in earlier)},
                          "packet_evaluation_at_decision": packet, "conditions":recorded_conditions(doc["text"]),
                          "basis": "synthetic-conditional-demonstration" if synthetic and all(synthetic) else "established" if result["admitted"] is not None else "missing-evidence",
                          "later_evidence_may_not_rewrite_this_evaluation":True})
    viewed, docs = visible(tables, documents, clock)
    apps = latest_applications(viewed["applications.csv"]);old = {a["application_id"]:a for a in previous["applications"]} if previous else {}
    cases = []
    for app_id, app in sorted(apps.items()):
        def presentation_at(stamp, revision):
            known = [d for d in decisions if d["result"]["admitted"] is True and d["fields"]["Body"] == "Governing Body" and d["fields"]["Application"] == app_id and d["fields"]["Revision"] == str(revision) and d["fields"]["Decision date"] <= stamp]
            return known[-1]["fields"]["Decision date"] if known else None
        case = evaluate(app, viewed, docs, clock, rules, policy, roster, presentation=presentation_at(clock,app["row"]["revision"]))
        if app_id in old:case["prior_monitored_conditions"] = old[app_id]["monitored_conditions"]
        case = finish_case(case, decisions, docs, viewed, clock, contract, rules, roster)
        for field, value in (("appointment_history",{"approval_decision_id":case["approval_decision_id"],"activation":case["activation"]}),
                             ("condition_history",case["monitored_conditions"])):
            prior = copy.deepcopy(old[app_id].get(field,[])) if app_id in old else []
            if not prior or prior[-1]["value"] != value:prior.append({"batch":batch,"as_of":clock,"value":copy.deepcopy(value)})
            case[field] = prior
        history = copy.deepcopy(old[app_id]["history"]) if app_id in old else []
        # Record new dated source/revision transitions, using only this batch's occurrences.
        dates = {o["row"].get(ROW_DATES.get(name)) for name,items in tables.items() for o in items if o["source"]["batch"] == batch and o["row"].get("application_id") == app_id and ROW_DATES.get(name)}
        dates |= {metadata(d["text"]).get("Date") for d in docs if d["source"]["batch"] == batch and metadata(d["text"]).get("Application") == app_id}
        dates.discard(None);dates.discard("")
        for stamp in sorted(dates | {clock}):
            partial, known_docs = visible(tables, documents, stamp)
            at = latest_applications(partial["applications.csv"]).get(app_id)
            if at is None:continue
            value = brief(evaluate(at, partial, known_docs, stamp, rules, policy, roster,presentation=presentation_at(stamp,at["row"]["revision"])))
            if not history or history[-1]["value"] != value:
                history.append({"batch":batch, "evidence_clock":stamp, "value":value,
                                "source_view": "only retained predecessor plus current batch dated evidence; not a revision of earlier reports"})
        case["history"] = history;cases.append(case)
    conflicts = [{"application_id":a["application_id"],"fields":a["schema_conflicts"]} for a in cases if a["schema_conflicts"]]
    return {"format":"credentialing-workflow/1", "engine":"workflow/1", "dataset":"synthetic-demonstration" if synthetic and all(synthetic) else "supplied-evidence", "batch":batch, "as_of":clock,
            "evidence_state_sha256":state_sha, "previous_workflow_sha256":previous_sha, "rules_sha256":rule_sha,
            "source_manifest":manifest, "applications":cases, "decision_history":decisions,
            "revision_history":revision_history(tables), "schema_projection_conflicts":conflicts,
            "assessment_state":"representable" if not conflicts else "blocked-at-schema-projection",
            "summary":{"applications":len(cases), "statuses":dict(Counter(a["status"] or "unresolved-intake-status" for a in cases)),
                       "packet_presentable":dict(Counter(str(a["packet"]["presentable"]) for a in cases)),
                       "admitted":sum(d["result"]["admitted"] is True for d in decisions),
                       "refused":sum(d["result"]["admitted"] is False for d in decisions),
                       "admission_unresolved":sum(d["result"]["admitted"] is None for d in decisions),
                       "schema_applications":sum(a["schema_application"] is not None for a in cases)}}
