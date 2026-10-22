"""Read-only schema/chain relationship verifier; never manufactures a snapshot."""

from datetime import date
from pathlib import Path

from .validation import GroundworkError, confined_file, digest, read_json, relative_path, schema_validate


def verify_snapshot(root: Path, path: str, schema: dict):
    if root.is_symlink():
        raise GroundworkError("unsafe_path", "Snapshot workspace cannot be symlinked")
    root = root.resolve(strict=True)
    seen_paths, seen_ids = set(), set()
    checked = []

    def check(name):
        relative_path(name)
        if name in seen_paths:
            raise GroundworkError("snapshot_chain", "Snapshot predecessor cycle")
        seen_paths.add(name)
        raw = confined_file(root, name).read_bytes()
        value = read_json(raw)
        schema_validate(value, schema)
        if value["snapshot_id"] in seen_ids:
            raise GroundworkError("snapshot_chain", "Snapshot occurrence ID is reused")
        seen_ids.add(value["snapshot_id"])
        if name not in value["produced"]:
            raise GroundworkError("snapshot_relationship", "Snapshot omits itself from produced")
        for file in value["produced"] + [value["rules_file"]]:
            confined_file(root, file)
        apps = {a["application_id"]: a for a in value["applications"]}
        if len(apps) != len(value["applications"]):
            raise GroundworkError("snapshot_relationship", "Application identifier repeats")
        for app in apps.values():
            decisions = {d["decision_id"]: d for d in app["decisions"]}
            if len(decisions) != len(app["decisions"]):
                raise GroundworkError("snapshot_relationship", "Decision identifier repeats")
            if any(d["admitted"] and d["reason"] is not None for d in decisions.values()):
                raise GroundworkError("snapshot_relationship", "Admitted decision carries refusal reason")
            approval = app["approval_decision_id"]
            if approval is not None and (approval not in decisions or not decisions[approval]["admitted"]):
                raise GroundworkError("snapshot_relationship", "Approval ID does not name an admitted same-file decision")
            activation = app["activation"]
            if activation is not None:
                if approval is None or activation["effective_date"] > activation["cycle_end"]:
                    raise GroundworkError("snapshot_relationship", "Activation lacks authority link or valid range")
                active = activation["effective_date"] <= value["as_of"] <= activation["cycle_end"]
                if activation["active_at_export"] != active:
                    raise GroundworkError("snapshot_relationship", "Activation flag contradicts export clock")
        prior = value["predecessor"]
        if prior is None:
            if value["batch"] != 1:
                raise GroundworkError("snapshot_chain", "Only batch one may omit predecessor")
        else:
            old_raw = confined_file(root, prior["path"]).read_bytes()
            if digest(old_raw) != prior["sha256"]:
                raise GroundworkError("snapshot_chain", "Predecessor hash differs from retained bytes")
            old = check(prior["path"])
            if value["batch"] != old["batch"] + 1 or value["as_of"] < old["as_of"]:
                raise GroundworkError("snapshot_chain", "Batch sequence or export clock regressed")
            current_apps = {a["application_id"]: a for a in value["applications"]}
            for before in old["applications"]:
                after = current_apps.get(before["application_id"])
                if after is None or after["revision"] < before["revision"]:
                    raise GroundworkError("snapshot_relationship", "Prior application/revision is lost")
                # Received decision order and refusal reasons survive continuation.
                retained = after["decisions"][:len(before["decisions"])]
                if retained != before["decisions"]:
                    raise GroundworkError("snapshot_relationship", "Prior decision history was removed or rewritten")
        checked.append({"path": name, "sha256": digest(raw), "batch": value["batch"], "as_of": value["as_of"]})
        return value

    check(path)
    return {"operation": "verify-snapshot", "structure_and_links": "valid", "checked": checked,
            "limitations": ["Does not prove completeness, CV reconciliation, packet facts or source authority",
                            "Does not prove exact grants, condition satisfaction, action ownership or consumed-file completeness",
                            "Schema/links alone do not establish submission readiness"]}
