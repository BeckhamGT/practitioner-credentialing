"""Schema/chain-gated snapshot publication with retained bytes and recovery.

Publication here means local file generation. Git commit seals an occurrence;
this module never commits, pushes, submits, or supplies missing business facts.
"""

from __future__ import annotations

import copy
import os
import tempfile
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from .snapshots import verify_snapshot
from .validation import (GroundworkError, confined_file, digest, json_bytes, read_json,
                         relative_path, schema_validate)


def snapshot_path(batch):
    return f"deliverables/snapshots/batch-{batch:02}.json"


def payload(value):
    # A new request ID/output list alone is not a changed business occurrence.
    return {k: v for k, v in value.items() if k not in ("snapshot_id", "produced", "predecessor")}


class SnapshotWriter:
    def __init__(self, root, schema):
        if root.is_symlink():
            raise GroundworkError("unsafe_path", "Writer root cannot be a symlink")
        self.root = root.resolve(strict=True)
        self.schema = schema
        self.control = self.root / ".local/snapshot-writer"

    def _target(self, name):
        relative_path(name)
        target = self.root
        for part in name.split("/"):
            target = target / part
            if target.is_symlink():
                raise GroundworkError("unsafe_path", "Symlinked writer destination")
        return target

    @contextmanager
    def _lock(self):
        self._target(".local/snapshot-writer").mkdir(parents=True, exist_ok=True)
        path = self.control / "lock"
        try:
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as exc:
            raise GroundworkError("writer_busy", "Writer lock exists; establish owner before recovery") from exc
        os.close(descriptor)
        try:
            yield
        finally:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass  # Do not misreport completed output as a failed transaction.

    @staticmethod
    def _atomic(path, raw):
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(prefix=".snapshot-", dir=path.parent)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(raw);stream.flush();os.fsync(stream.fileno())
            os.replace(temporary, path)
        finally:
            Path(temporary).unlink(missing_ok=True)

    def _old(self):
        folder = self._target("deliverables/snapshots")
        result = {}
        if folder.exists():
            for path in folder.glob("batch-*.json"):
                name = path.relative_to(self.root).as_posix()
                raw = confined_file(self.root, name).read_bytes();value = read_json(raw)
                schema_validate(value, self.schema)
                if name != snapshot_path(value["batch"]) or value["batch"] in result:
                    raise GroundworkError("snapshot_chain", "Ambiguous current snapshot occurrence")
                result[value["batch"]] = (value, raw)
        if result:
            verify_snapshot(self.root, snapshot_path(max(result)), self.schema)
        return result

    def publish(self, candidates, clocks, unresolved, reason=None):
        if unresolved:
            raise GroundworkError("snapshot_unrepresentable", "Required business fields are uncomputed; no truthful schema projection")
        if not candidates:
            raise GroundworkError("writer_input", "No candidate supplied")
        with self._lock():
            if (self.control / "active.json").exists():
                raise GroundworkError("writer_recovery_required", "Preserve interrupted transaction and recover before retry")
            old = self._old()
            ordered = sorted(copy.deepcopy(candidates), key=lambda c: c["batch"])
            by_batch = {c["batch"]: c for c in ordered}
            if len(by_batch) != len(ordered):
                raise GroundworkError("writer_input", "Repeated candidate batch")
            for candidate in ordered:
                schema_validate(candidate, self.schema)
                if clocks.get(candidate["batch"]) != candidate["as_of"]:
                    raise GroundworkError("snapshot_clock", "Candidate clock differs from its source export")
            changed = [c["batch"] for c in ordered if c["batch"] not in old or payload(c) != payload(old[c["batch"]][0])]
            if not changed:
                return {"result": "unchanged", "snapshots": [snapshot_path(c["batch"]) for c in ordered],
                        "written": [], "sealed_by_git_commit": False}
            first = min(changed);last = max(max(old, default=0), max(by_batch))
            if set(range(first, last + 1)) - by_batch.keys():
                raise GroundworkError("downstream_regeneration", "Changed occurrence requires every later snapshot in the chain")
            if first > 1 and first - 1 not in old and first - 1 not in by_batch:
                raise GroundworkError("snapshot_chain", "Predecessor snapshot missing")
            if any(batch in old for batch in range(first, last + 1)) and not reason:
                raise GroundworkError("supersession_reason", "Preserve a reason for changing retained occurrences")
            archive = {}
            registry_path = "deliverables/snapshots/history/index.json"
            registry_file = self._target(registry_path)
            registry = read_json(registry_file.read_bytes()) if registry_file.exists() else {"format": "snapshot-history/1", "occurrences": []}
            ids = {v[0]["snapshot_id"] for v in old.values()} | {x["snapshot_id"] for x in registry["occurrences"]}
            for batch in range(first, last + 1):
                candidate = by_batch[batch]
                if candidate["snapshot_id"] in ids:
                    raise GroundworkError("snapshot_id_reused", "Changed/retained occurrences need distinct IDs")
                ids.add(candidate["snapshot_id"])
                if batch in old:
                    value, raw = old[batch];sha = digest(raw)
                    path = f"deliverables/snapshots/history/batch-{batch:02}-{sha}.json"
                    existing = self._target(path)
                    if existing.exists() and existing.read_bytes() != raw:
                        raise GroundworkError("snapshot_history", "Retained archive differs from expected original bytes")
                    archive[path] = raw
                    if not any(x["sha256"] == sha for x in registry["occurrences"]):
                        registry["occurrences"].append({"original_path": snapshot_path(batch), "retained_path": path,
                                                        "sha256": sha, "snapshot_id": value["snapshot_id"], "reason": reason})
            output_names = [snapshot_path(b) for b in range(first, last + 1)] + sorted(archive) + ["deliverables/run-log.md"]
            if archive:
                output_names.append(registry_path)
            planned = dict(archive)
            previous_raw = old[first - 1][1] if first > 1 else None
            for batch in range(first, last + 1):
                candidate = by_batch[batch]
                candidate["predecessor"] = {"path": snapshot_path(batch - 1), "sha256": digest(previous_raw)} if previous_raw is not None else None
                candidate["produced"] = sorted(output_names)
                previous_raw = json_bytes(candidate)
                planned[snapshot_path(batch)] = previous_raw
            if archive:
                planned[registry_path] = json_bytes(registry)
            log_path = "deliverables/run-log.md"
            prior_log = self._target(log_path).read_bytes() if self._target(log_path).exists() else b"# Snapshot generation log\n"
            note = ("\n- " + datetime.now(timezone.utc).isoformat() + ": local snapshot generation batches "
                    + str(first) + "–" + str(last) + "; reason: " + (reason or "new continuation")
                    + "; written=" + ", ".join(sorted(output_names)) + "; Git sealing is separate.\n")
            planned[log_path] = prior_log + note.encode()
            # Verify prospective relationships in isolation before changing outputs.
            with tempfile.TemporaryDirectory(dir=self.control, prefix="preflight-") as name:
                temp = Path(name)
                required = set()
                for value, _ in old.values():
                    required.update(value["produced"]);required.add(value["rules_file"])
                for candidate in ordered:
                    required.add(candidate["rules_file"])
                for path in required:
                    if path not in planned:
                        raw = confined_file(self.root, path).read_bytes()
                        target = temp / relative_path(path);target.parent.mkdir(parents=True, exist_ok=True);target.write_bytes(raw)
                for path, raw in planned.items():
                    self._target(path)
                    target = temp / relative_path(path);target.parent.mkdir(parents=True, exist_ok=True);target.write_bytes(raw)
                for batch in range(first, last + 1):
                    verify_snapshot(temp, snapshot_path(batch), self.schema)
            self._transaction(planned)
            return {"result": "written", "snapshots": [snapshot_path(b) for b in range(first, last + 1)],
                    "written": sorted(output_names), "retained": sorted(archive), "sealed_by_git_commit": False}

    def _transaction(self, planned):
        name = "transactions/" + uuid.uuid4().hex
        directory = self.control / name;directory.mkdir(parents=True)
        manifest = {"format": "snapshot-transaction/1", "status": "prepared", "files": []}
        for index, (path, raw) in enumerate(sorted(planned.items())):
            target = self._target(path);old = target.read_bytes() if target.exists() else None
            (directory / f"new-{index}").write_bytes(raw)
            if old is not None:
                (directory / f"old-{index}").write_bytes(old)
            manifest["files"].append({"path": path, "index": index, "new_sha256": digest(raw),
                                      "old_sha256": digest(old) if old is not None else None})
        (directory / "manifest.json").write_bytes(json_bytes(manifest))
        active = self.control / "active.json"
        self._atomic(active, json_bytes({"transaction": name}))
        try:
            for entry in manifest["files"]:
                self._atomic(self._target(entry["path"]), (directory / f"new-{entry['index']}").read_bytes())
        except OSError as exc:
            manifest["status"] = "failed-recovery-required"
            (directory / "manifest.json").write_bytes(json_bytes(manifest))
            raise GroundworkError("writer_interrupted", "Snapshot transaction interrupted; do not expose partial working files as sealed; recover from retained transaction") from exc
        manifest["status"] = "completed"
        (directory / "manifest.json").write_bytes(json_bytes(manifest));active.unlink()

    def recover(self):
        """Restore prior bytes after validating every current/retained object."""
        with self._lock():
            active = self.control / "active.json"
            if not active.exists():
                raise GroundworkError("writer_recovery", "No interrupted snapshot transaction")
            pointer = read_json(active.read_bytes())["transaction"]
            relative_path(pointer)
            manifest_path = confined_file(self.control, pointer + "/manifest.json")
            directory = manifest_path.parent;manifest = read_json(manifest_path.read_bytes())
            if manifest.get("format") != "snapshot-transaction/1":
                raise GroundworkError("writer_recovery", "Unknown transaction format")
            restore = []
            for entry in manifest["files"]:
                new = confined_file(directory, f"new-{entry['index']}").read_bytes()
                old = confined_file(directory, f"old-{entry['index']}").read_bytes() if entry["old_sha256"] is not None else None
                if digest(new) != entry["new_sha256"] or (old is not None and digest(old) != entry["old_sha256"]):
                    raise GroundworkError("writer_recovery", "Transaction retained bytes are corrupt; preserve and investigate")
                target = self._target(entry["path"])
                current = digest(target.read_bytes()) if target.exists() else None
                if current not in (entry["old_sha256"], entry["new_sha256"]):
                    raise GroundworkError("writer_recovery", "Output changed outside transaction; manual investigation required")
                restore.append((target, old))
            for target, old in restore:
                if old is None:
                    target.unlink(missing_ok=True)
                else:
                    self._atomic(target, old)
            manifest["status"] = "rolled-back-retained"
            manifest_path.write_bytes(json_bytes(manifest));active.unlink()
            return {"result": "rolled-back", "transaction_retained": pointer, "prior_outputs_restored": True}
