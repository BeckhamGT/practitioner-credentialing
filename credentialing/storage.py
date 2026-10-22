"""Content-addressed evidence state, with an atomic local HEAD commit point."""

from __future__ import annotations

import os
import tempfile
from contextlib import contextmanager
from pathlib import Path

from .validation import (GroundworkError, HEAD_SCHEMA, STATE_SCHEMA, confined_file,
                         digest, json_bytes, manifest_validate, read_json,
                         schema_validate, validate_content)


class Store:
    def __init__(self, root: Path):
        if root.is_symlink():
            raise GroundworkError("unsafe_path", "State root cannot be a symlink")
        self.root = root.resolve()

    def _object(self, kind: str, sha: str) -> bytes:
        schema_validate(sha, {"type": "string", "pattern": "^[0-9a-f]{64}$"})
        raw = confined_file(self.root, f"objects/{kind}/{sha}").read_bytes()
        if digest(raw) != sha:
            raise GroundworkError("corrupt_state", f"Content hash mismatch in {kind} object")
        return raw

    def current(self):
        if (self.root / "objects").is_symlink():
            raise GroundworkError("unsafe_path", "State object directory cannot be a symlink")
        head_path = self.root / "HEAD.json"
        if head_path.is_symlink():
            raise GroundworkError("unsafe_path", "State HEAD cannot be a symlink")
        if not head_path.exists():
            # Lost HEAD and an abandoned initial candidate are ambiguous. Do not
            # silently initialize over either one or promote an orphan object.
            states = self.root / "objects" / "states"
            if states.is_symlink() or (states.exists() and any(states.iterdir())):
                raise GroundworkError("missing_state", "State objects exist without HEAD; preserve them and investigate")
            return None
        head = read_json(head_path.read_bytes())
        schema_validate(head, HEAD_SCHEMA)
        return self.at(head["sha256"])

    def at(self, state_sha256: str):
        """Read only this occurrence and its predecessors, never a newer HEAD."""
        chain = []
        visited = set()
        sha = state_sha256
        while sha is not None:
            if sha in visited:
                raise GroundworkError("corrupt_state", "State chain contains a cycle")
            visited.add(sha)
            state = read_json(self._object("states", sha))
            schema_validate(state, STATE_SCHEMA)
            manifest = state["manifest"]
            manifest_validate(manifest)
            manifest_raw = self._object("blobs", state["manifest_sha256"])
            if read_json(manifest_raw) != manifest:
                raise GroundworkError("corrupt_state", "Stored manifest disagrees with retained original")
            contents = {f["path"]: self._object("blobs", f["sha256"]) for f in manifest["files"]}
            summary = validate_content(manifest, contents)
            chain.append((sha, state, summary))
            sha = state["previous_state_sha256"]
        ordered = list(reversed(chain))
        previous_date = None
        for batch, (_, state, _) in enumerate(ordered, 1):
            manifest = state["manifest"]
            if manifest["batch"] != batch or (previous_date and manifest["as_of"] < previous_date):
                raise GroundworkError("corrupt_state", "State sequence or export clock is invalid")
            previous_date = manifest["as_of"]
        return {"sha256": state_sha256, "state": chain[0][1], "summary": chain[0][2], "chain": ordered}

    def blob(self, sha256: str) -> bytes:
        """Read a hash-verified retained source, without touching HEAD."""
        return self._object("blobs", sha256)

    @contextmanager
    def locked(self):
        self.root.mkdir(parents=True, exist_ok=True)
        lock = self.root / ".write-lock"
        try:
            fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError as exc:
            raise GroundworkError("store_busy", "State store is locked; do not remove a live writer's lock") from exc
        try:
            os.close(fd)
            yield
        finally:
            # Cleanup failure after the commit point must not misreport a
            # committed operation as failed. A remaining lock requires review.
            try:
                lock.unlink()
            except OSError:
                pass

    def _put(self, kind: str, raw: bytes) -> str:
        sha = digest(raw)
        directory = self.root / "objects" / kind
        for component in (self.root / "objects", directory):
            if component.is_symlink():
                raise GroundworkError("unsafe_path", "State object directory cannot be a symlink")
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / sha
        try:
            with path.open("xb") as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
        except FileExistsError:
            if path.is_symlink() or path.read_bytes() != raw:
                raise GroundworkError("corrupt_state", "An immutable object differs from its expected bytes")
        return sha

    def _replace_head(self, sha: str) -> None:
        raw = json_bytes({"format": "credentialing-groundwork-head/1", "sha256": sha})
        fd, name = tempfile.mkstemp(prefix=".head-", dir=self.root)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, self.root / "HEAD.json")
        finally:
            if os.path.exists(name):
                os.unlink(name)

    def stage(self, manifest: dict, manifest_raw: bytes, contents: dict[str, bytes], previous: str | None):
        manifest_validate(manifest)
        validate_content(manifest, contents)
        with self.locked():
            current = self.current()
            batch = manifest["batch"]
            manifest_sha = digest(manifest_raw)
            if current and batch == current["state"]["manifest"]["batch"]:
                old = current["state"]
                if manifest_sha == old["manifest_sha256"] and previous == old["previous_state_sha256"]:
                    return self._receipt(current["sha256"], manifest, "unchanged")
                raise GroundworkError("changed_batch", "Retained batch differs; preserve store and use a separate reconstruction")
            expected = current["state"]["manifest"]["batch"] + 1 if current else 1
            if batch != expected:
                raise GroundworkError("batch_sequence", "Only the next batch can extend retained state")
            expected_previous = current["sha256"] if current else None
            if previous != expected_previous:
                raise GroundworkError("predecessor_mismatch", "Explicit previous state does not match verified current state")
            if current and manifest["as_of"] < current["state"]["manifest"]["as_of"]:
                raise GroundworkError("clock_regression", "Export date cannot move backwards")
            # Validate before writing immutable objects or moving HEAD.
            manifest_validate(manifest, batch)
            validate_content(manifest, contents)
            if read_json(manifest_raw) != manifest:
                raise GroundworkError("invalid_structure", "Manifest bytes and parsed manifest disagree")
            for raw in contents.values():
                self._put("blobs", raw)
            self._put("blobs", manifest_raw)
            state = {"format": "credentialing-groundwork-state/1", "phase": "evidence-only",
                     "business_blockers": ["G1", "G2"], "previous_state_sha256": previous,
                     "manifest_sha256": manifest_sha, "manifest": manifest}
            schema_validate(state, STATE_SCHEMA)
            sha = self._put("states", json_bytes(state))
            receipt = self._receipt(sha, manifest, "staged")
            self._replace_head(sha)  # Last fallible operation; this is the commit point.
            return receipt

    @staticmethod
    def _receipt(sha: str, manifest: dict, result: str):
        return {"operation": "evidence-stage", "result": result, "state_sha256": sha,
                "batch": manifest["batch"], "as_of": manifest["as_of"],
                "phase": "evidence-only", "business_blockers": ["G1", "G2"],
                "assessed_snapshot_written": False}
