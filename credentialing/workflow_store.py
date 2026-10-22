"""Immutable internal workflow results, separate from evidence and schema snapshots."""

import os
import tempfile
from pathlib import Path

from .validation import GroundworkError, confined_file, digest, json_bytes, read_json


class WorkflowStore:
    def __init__(self, root):
        if root.is_symlink():raise GroundworkError("unsafe_path", "Workflow store cannot be symlinked")
        self.root = root.resolve()

    def at(self, sha):
        if not isinstance(sha,str) or len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
            raise GroundworkError("workflow_hash", "Invalid workflow occurrence hash")
        raw = confined_file(self.root, "objects/"+sha+".json").read_bytes()
        if digest(raw) != sha:raise GroundworkError("workflow_corrupt", "Workflow result differs from its content hash")
        value = read_json(raw)
        if value.get("format") != "credentialing-workflow/1":raise GroundworkError("workflow_corrupt", "Unknown workflow format")
        return value

    def current(self):
        path = self.root / "HEAD.json"
        if path.is_symlink() or (self.root/"objects").is_symlink():raise GroundworkError("unsafe_path", "Symlinked workflow objects/HEAD")
        if not path.exists():
            if (self.root/"objects").exists() and any((self.root/"objects").iterdir()):
                raise GroundworkError("workflow_missing_head", "Preserve workflow objects without HEAD; do not initialize over them")
            return None
        head = read_json(path.read_bytes());sha = head["sha256"];result = self.at(sha)
        seen = {sha};cursor = result
        while cursor["previous_workflow_sha256"]:
            before = cursor["previous_workflow_sha256"]
            if before in seen:raise GroundworkError("workflow_corrupt", "Workflow predecessor cycle")
            seen.add(before);prior = self.at(before)
            if prior["batch"]+1 != cursor["batch"] or prior["as_of"] > cursor["as_of"]:
                raise GroundworkError("workflow_corrupt", "Workflow sequence/clock regressed")
            cursor = prior
        if cursor["batch"] != 1:raise GroundworkError("workflow_corrupt", "Workflow chain does not start at batch one")
        return sha,result

    def predecessor(self, batch, state_sha, explicit):
        current = self.current()
        if current and current[1]["batch"] == batch:
            if current[1]["evidence_state_sha256"] != state_sha or current[1]["previous_workflow_sha256"] != explicit:
                raise GroundworkError("workflow_predecessor", "Changed rerun input; preserve current workflow and reconstruct separately")
            return self.at(explicit) if explicit else None
        if batch != (current[1]["batch"]+1 if current else 1) or explicit != (current[0] if current else None):
            raise GroundworkError("workflow_predecessor", "Supply exact current workflow predecessor and next batch")
        return current[1] if current else None

    def commit(self, report):
        self.root.mkdir(parents=True,exist_ok=True)
        lock = self.root / ".write-lock"
        try:fd = os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        except FileExistsError as exc:raise GroundworkError("workflow_busy", "Workflow writer is active or needs investigation") from exc
        os.close(fd)
        try:
            self.predecessor(report["batch"],report["evidence_state_sha256"],report["previous_workflow_sha256"])
            raw = json_bytes(report);sha = digest(raw);current = self.current()
            if current and current[1]["batch"] == report["batch"]:
                if current[0] != sha:raise GroundworkError("workflow_changed", "Changed retained result; use separate reconstruction, never overwrite")
                return sha,"unchanged"
            objects = self.root/"objects";objects.mkdir(exist_ok=True);path = objects/(sha+".json")
            if path.exists():
                if path.is_symlink() or path.read_bytes()!=raw:raise GroundworkError("workflow_corrupt", "Existing workflow object differs")
            else:
                with path.open("xb") as out:out.write(raw);out.flush();os.fsync(out.fileno())
            descriptor,name = tempfile.mkstemp(prefix=".head-",dir=self.root)
            try:
                with os.fdopen(descriptor,"wb") as out:out.write(json_bytes({"format":"workflow-head/1","sha256":sha}));out.flush();os.fsync(out.fileno())
                os.replace(name,self.root/"HEAD.json")
            finally:Path(name).unlink(missing_ok=True)
            return sha,"stored"
        finally:
            try:lock.unlink()
            except OSError:pass
