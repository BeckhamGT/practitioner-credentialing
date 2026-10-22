"""Read typed, source-linked MSP observations; never synthesize a human record."""

import json
import re

from .review import metadata
from .validation import GroundworkError, read_json


BOOL_FACTS = {"application_signature", "cv_current", "cv_reconciled", "all_credentials_declared"}
ENTRY_FACTS = {"accreditation_by_entry", "secondary_route_by_entry"}
CORRECTIONS = {"resolved_source_concerns"}


def observations(documents, app_id, revision, roster_text):
    """Adapter for an actual MSP review record, not a switch on the run command.

Every cited document must already be in the dated visible evidence set. A named
role is checked against the retained roster. Source authenticity remains that
of the authorized input package; a hash authenticates bytes, not a person.
"""
    available = {(d["source"]["path"], d["source"]["sha256"]): d for d in documents}
    found = {}
    for document in sorted(documents, key=lambda d:(metadata(d["text"]).get("Date", ""), d["source"]["batch"], d["source"]["path"])):
        fields = metadata(document["text"])
        if fields.get("Review schema") != "credentialing-observations/1":
            continue
        if fields.get("Application") != app_id or fields.get("Revision") != str(revision):
            continue
        actor = fields.get("Recorded by", "")
        if (not actor or f"Medical Services Professional\n{actor}\ncontinuing" not in roster_text
                or not fields.get("Date")):
            raise GroundworkError("human_observation_authority", "MSP observation is not bound to the roster/date")
        blocks = re.findall(r"```json\s*\n(.*?)\n```", document["text"], re.S)
        if len(blocks) != 1:
            raise GroundworkError("human_observation", "One typed JSON observation block is required")
        try:
            value = read_json(blocks[0].encode())
        except ValueError as exc:
            raise GroundworkError("human_observation", "Invalid observation JSON") from exc
        if set(value) != {"evidence", "facts"} or not isinstance(value["evidence"], list) or not value["evidence"]:
            raise GroundworkError("human_observation", "Facts require explicit source document paths and hashes")
        for ref in value["evidence"]:
            if set(ref) != {"path", "sha256"} or (ref["path"], ref["sha256"]) not in available:
                raise GroundworkError("human_observation", "Cited observation evidence is not in the dated input")
            target = available[(ref["path"], ref["sha256"])]
            if metadata(target["text"]).get("Application") != app_id:
                raise GroundworkError("human_observation", "Cited document belongs to another application")
            if fields["Date"] < metadata(target["text"]).get("Date", fields["Date"]):
                raise GroundworkError("human_observation", "Review predates the evidence it claims to inspect")
        facts = value["facts"]
        if not isinstance(facts, dict) or set(facts) - BOOL_FACTS - ENTRY_FACTS - CORRECTIONS:
            raise GroundworkError("human_observation", "Observation cannot grant, waive or make a reserved judgment")
        for key, item in facts.items():
            if key in BOOL_FACTS and type(item) is not bool:
                raise GroundworkError("human_observation", "Observation fact must be an explicit boolean")
            if key in ENTRY_FACTS and (not isinstance(item, dict) or any(type(v) is not bool for v in item.values())):
                raise GroundworkError("human_observation", "Entry observations require explicit ID/boolean pairs")
            if key in CORRECTIONS:
                references = {r["sha256"]:available[(r["path"],r["sha256"])] for r in value["evidence"]}
                if not isinstance(item,dict) or any(not isinstance(sha,str) or not isinstance(correction,str) or sha==correction or sha not in references or correction not in references for sha,correction in item.items()):
                    raise GroundworkError("human_observation", "A concern resolution requires original and distinct correcting source hashes, both explicitly cited")
                if any(metadata(references[c]["text"]).get("Date","") < metadata(references[s]["text"]).get("Date","") for s,c in item.items()):
                    raise GroundworkError("human_observation", "Correcting source predates its concern")
            provenance = {"source": document["source"], "date": fields["Date"], "actor":actor, "evidence":value["evidence"]}
            item_sources = {}
            if key in ENTRY_FACTS | CORRECTIONS:
                before = found.get(key,{"value":{},"item_sources":{}})
                for identity in before["value"].keys() & item.keys():
                    if before["value"][identity] != item[identity] and fields.get("Supersedes review") != before["item_sources"][identity]["source"]["sha256"]:
                        raise GroundworkError("human_observation_conflict", "Changed entry observation requires its own prior review hash")
                item_sources = {**before["item_sources"], **{identity:provenance for identity in item}}
                item = {**before["value"],**item}
            elif key in found and found[key]["value"] != item and fields.get("Supersedes review") != found[key]["source"]["sha256"]:
                raise GroundworkError("human_observation_conflict", "Conflicting human observations need a linked correction, not silent selection")
            found[key] = {"value":item, **provenance, "item_sources":item_sources, "classification":"human-recorded-source-observation"}
    return found
