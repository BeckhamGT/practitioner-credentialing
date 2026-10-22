"""Local structural validation; no completeness or clinical judgments."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from datetime import date
from pathlib import Path, PurePosixPath

from jsonschema import Draft202012Validator, FormatChecker


class GroundworkError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise GroundworkError("invalid_json", "Duplicate JSON object key")
        result[key] = value
    return result


def read_json(data: bytes):
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=_unique_object,
                          parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Non-finite JSON")))
    except (ValueError, UnicodeError) as exc:
        raise GroundworkError("invalid_json", "Expected strict UTF-8 JSON") from exc


def schema_validate(value, schema: dict) -> None:
    errors = sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value),
                    key=lambda e: str(list(e.path)))
    if errors:
        # Do not echo sensitive source values into command/error logs.
        path = "/".join(map(str, errors[0].path)) or "<root>"
        raise GroundworkError("invalid_structure", f"Schema validation failed at {path}: {errors[0].validator}")


SHA = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
DAY = {"type": "string", "format": "date", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"}
FILE_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["path", "sha256", "source_id", "source_url", "source_batch", "kind"],
    "properties": {
        "path": {"type": "string", "minLength": 1}, "sha256": SHA,
        "source_id": {"type": "string", "minLength": 1},
        "source_url": {"type": "string", "pattern": "^https://[^\\s]+$"},
        "source_batch": {"type": "integer", "minimum": 1},
        "kind": {"enum": ["records", "document", "batch-readme"]},
    },
}
MANIFEST_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object", "additionalProperties": False,
    "required": ["format", "batch", "as_of", "files"],
    "properties": {
        "format": {"const": "credentialing-input-manifest/1"},
        "batch": {"type": "integer", "minimum": 1}, "as_of": DAY,
        "files": {"type": "array", "minItems": 14, "items": FILE_SCHEMA},
    },
}
STATE_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object", "additionalProperties": False,
    "required": ["format", "phase", "business_blockers", "previous_state_sha256", "manifest_sha256", "manifest"],
    "properties": {
        "format": {"const": "credentialing-groundwork-state/1"},
        "phase": {"const": "evidence-only"},
        "business_blockers": {"const": ["G1", "G2"]},
        "previous_state_sha256": {"oneOf": [{"type": "null"}, SHA]},
        "manifest_sha256": SHA, "manifest": MANIFEST_SCHEMA,
    },
}
HEAD_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["format", "sha256"],
    "properties": {"format": {"const": "credentialing-groundwork-head/1"}, "sha256": SHA},
}


def relative_path(value: str) -> str:
    parts = value.split("/")
    if (not value or "\\" in value or "\x00" in value or ":" in value
            or any(part in ("", ".", "..") for part in parts)
            or PurePosixPath(value).is_absolute()):
        raise GroundworkError("unsafe_path", "Source paths must be canonical relative POSIX paths")
    return value


def confined_file(root: Path, name: str) -> Path:
    relative_path(name)
    path = root
    for part in name.split("/"):
        path = path / part
        if path.is_symlink():
            raise GroundworkError("unsafe_path", "Symlinked input/store paths are not accepted")
    if not path.is_relative_to(root) or not path.is_file():
        raise GroundworkError("missing_file", f"Required file not found: {name}")
    return path


def manifest_validate(manifest: dict, expected_batch: int | None = None) -> None:
    schema_validate(manifest, MANIFEST_SCHEMA)
    if expected_batch is not None and manifest["batch"] != expected_batch:
        raise GroundworkError("wrong_batch", "Manifest does not identify the requested batch")
    seen = set()
    source_ids = set()
    for entry in manifest["files"]:
        path = relative_path(entry["path"])
        if path.casefold() in seen or entry["source_id"] in source_ids:
            raise GroundworkError("duplicate_source", "Duplicate source path or source identifier")
        seen.add(path.casefold())
        source_ids.add(entry["source_id"])
        if entry["source_batch"] != manifest["batch"]:
            raise GroundworkError("wrong_batch", "Source provenance crosses the requested batch boundary")
    records = {f["path"] for f in manifest["files"] if f["kind"] == "records"}
    if records != set(LAYOUT):
        raise GroundworkError("record_set", "The thirteen required record files must be listed exactly")
    readmes = [f["path"] for f in manifest["files"] if f["kind"] == "batch-readme"]
    if readmes != ["README.md"]:
        raise GroundworkError("batch_readme", "Exactly one batch README.md is required")
    for entry in manifest["files"]:
        if entry["kind"] == "document" and not re.fullmatch(r"(?:letters|dispositions|decisions)/[^/]+\.md", entry["path"]):
            raise GroundworkError("document_path", "Supporting document must use its office folder and Markdown name")


# Column contracts are copied from all three observed office export headers, not
# guessed from a business outcome. All raw cells remain strings, including blanks.
LAYOUT = {
    "applications.csv": "application_id,revision,applicant_id,received_date,first_received_date,last_name,first_name,middle_name,birth_year,degree,npi,practice_state,position_sought,discipline,release_signed_date,cv_received_date,revision_reason",
    "application-disclosures.csv": "application_id,revision,question_code,question_text,answer,applicant_comment",
    "declared-history.csv": "entry_id,application_id,revision,entry_type,organization,location,role,from_date,to_date,hours_per_week,contact_name,contact_email,notes",
    "declared-credentials.csv": "declaration_id,application_id,revision,credential_class,issuer,jurisdiction_or_board,number_declared,declared_status,declared_issue_date,declared_expiry_date",
    "privilege-requests.csv": "request_id,application_id,revision,privilege_code,privilege_name,criteria_version_cited",
    "licence-lookup-wa.csv": "credentialnumber,credentialtype,status,firstissuedate,lastissuedate,expirationdate,ceduedate,actiontaken,birthyear,firstname,middlename,lastname,lookup_date",
    "licence-lookup-other-states.csv": "board_state,licence_number,licensee_name,licence_type,status,issue_date,expiry_date,disciplinary_action,verified_by,lookup_date",
    "certification-replies.csv": "reply_id,application_id,declaration_id,board_name,board_code,received_from,certificate_specialty,certification_status,initial_certification_date,expiry_date,requested_date,received_date,reply_method,notes",
    "verification-replies.csv": "reply_id,application_id,entry_id,element,attester_organization,attester_name,attester_role,received_from,verified_credential,verified_from,verified_to,outcome,requested_date,received_date,reply_method,notes",
    "verification-attempts.csv": "attempt_id,application_id,element,subject_ref,attempted_with,attempt_date,method,outcome,comment",
    "peer-referees.csv": "referee_id,application_id,revision,referee_name,referee_credential,referee_organization,referee_specialty,relationship_declared,source,first_request_date",
    "peer-reference-replies.csv": "reply_id,referee_id,application_id,signature_date,received_date,related_or_partner,relationship_stated,referee_specialty_stated,last_worked_together_end,recommendation,comments",
    "correspondence.csv": "letter_id,date,direction,application_id,correspondent,subject,document_path",
}
OBSERVATION_DATES = {"received_date", "first_received_date", "lookup_date", "attempt_date", "requested_date",
                     "signature_date", "first_request_date", "release_signed_date", "cv_received_date", "date"}


def checked_date(value: str, as_of: date, location: str) -> None:
    if not value:
        return  # Missing evidence stays missing; this layer assigns no meaning.
    try:
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
            raise ValueError("date shape")
        observed = date.fromisoformat(value)
    except ValueError as exc:
        raise GroundworkError("invalid_date", f"Invalid observation date at {location}") from exc
    if observed > as_of:
        raise GroundworkError("future_evidence", f"Observation after export date at {location}")


def validate_content(manifest: dict, contents: dict[str, bytes]) -> dict:
    """Validate bytes captured from the allowlist without reading other files."""
    manifest_validate(manifest)
    if set(contents) != {entry["path"] for entry in manifest["files"]}:
        raise GroundworkError("source_set", "Only the manifest's exact allowlist may enter state")
    as_of = date.fromisoformat(manifest["as_of"])
    counts = {}
    document_paths = {f["path"] for f in manifest["files"] if f["kind"] == "document"}
    indexed_documents = []
    for entry in manifest["files"]:
        name = entry["path"]
        raw = contents[name]
        if digest(raw) != entry["sha256"]:
            raise GroundworkError("hash_mismatch", f"Source bytes differ from manifest: {name}")
        try:
            text = raw.decode("utf-8")
        except UnicodeError as exc:
            raise GroundworkError("invalid_encoding", f"Source is not UTF-8: {name}") from exc
        if entry["kind"] == "records":
            try:
                reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
                if reader.fieldnames != LAYOUT[name].split(","):
                    raise GroundworkError("csv_header", f"Unexpected CSV columns: {name}")
                rows = list(reader)
                for number, row in enumerate(rows, 2):
                    if None in row or any(value is None for value in row.values()):
                        raise GroundworkError("csv_width", f"Malformed CSV row: {name}:{number}")
                    for column in OBSERVATION_DATES & row.keys():
                        checked_date(row[column], as_of, f"{name}:{number}:{column}")
                    if name == "correspondence.csv":
                        indexed_documents.append(relative_path(row["document_path"]))
                counts[name] = len(rows)
            except csv.Error as exc:
                raise GroundworkError("invalid_csv", f"Invalid CSV syntax: {name}") from exc
        elif entry["kind"] == "batch-readme":
            dates = re.findall(r"\*\*Export date: ([0-9]{4}-[0-9]{2}-[0-9]{2})\*\*", text)
            batches = re.findall(r"^# Batch ([0-9]+) export", text, re.MULTILINE)
            if dates != [manifest["as_of"]] or batches != [str(manifest["batch"])]:
                raise GroundworkError("batch_readme", "Batch README identity/clock differs from manifest")
        else:
            for label, value in re.findall(r"^\*\*(Date|Decision date):\*\*\s*([^\r\n]*)", text, re.MULTILINE):
                checked_date(value.strip(), as_of, f"{name}:{label}")
    if set(indexed_documents) != document_paths or len(indexed_documents) != len(set(indexed_documents)):
        raise GroundworkError("document_index", "Correspondence index and supporting document allowlist differ")
    return {"record_counts": dict(sorted(counts.items())), "documents": len(document_paths)}


def load_batch(root: Path, expected_batch: int):
    if root.is_symlink():
        raise GroundworkError("unsafe_path", "Batch root cannot be a symlink")
    root = root.resolve(strict=True)
    manifest_raw = confined_file(root, "input.manifest.json").read_bytes()
    manifest = read_json(manifest_raw)
    manifest_validate(manifest, expected_batch)  # Reject wrong provenance before source reads.
    contents = {f["path"]: confined_file(root, f["path"]).read_bytes() for f in manifest["files"]}
    summary = validate_content(manifest, contents)
    return manifest, manifest_raw, contents, summary
