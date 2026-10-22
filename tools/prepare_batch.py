"""Materialize one reviewed input manifest from retained extracted source text.

This preparation utility is outside the business runtime. stage/review/timeline
never open the combined archive. No network access or source rewriting occurs.
"""

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path, PurePosixPath


def prepare(archive_path, manifest_path, output):
    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw)
    archive = json.loads(archive_path.read_bytes())
    batch = manifest["batch"]
    lookup = {}
    for reading in archive["readings"]:
        if reading.get("batch") != batch:
            continue
        key = (reading["id"], reading["path"])
        if key in lookup:
            raise ValueError("Ambiguous source archive occurrence")
        lookup[key] = reading
    contents = {}
    for source in manifest["files"]:
        name = source["path"]
        parts = name.split("/")
        if (not name or "\\" in name or ":" in name or "\x00" in name or PurePosixPath(name).is_absolute()
                or any(p in ("", ".", "..") for p in parts) or name in contents):
            raise ValueError("Unsafe or repeated manifest path")
        if source["source_batch"] != batch:
            raise ValueError("Manifest source crosses batch boundary")
        reading = lookup.get((source["source_id"], f"batch-{batch:02}/" + name))
        if reading is None or reading["url"] != source["source_url"]:
            raise ValueError("Manifest source is absent or has different provenance")
        raw = reading["content"].encode("utf-8")
        if hashlib.sha256(raw).hexdigest() != source["sha256"]:
            raise ValueError("Source bytes differ from reviewed manifest")
        contents[name] = raw
    contents["input.manifest.json"] = manifest_raw
    output = Path(output)
    if output.is_symlink() or any(p.is_symlink() for p in output.parents):
        raise ValueError("Symlinked output path")
    if output.exists():
        for name, raw in contents.items():
            target = output / name
            if any(p.is_symlink() for p in [target, *target.parents]) or target.read_bytes() != raw:
                raise ValueError("Existing input differs; preserve it and select another output")
        return "unchanged"
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".prepared-", dir=output.parent))
    try:
        for name, raw in contents.items():
            path = temporary / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        os.rename(temporary, output)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return "prepared"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps({"operation": "prepare-input", "result": prepare(args.archive, args.manifest, args.output),
                      "scope": "one manifest-selected batch of extracted text, not original provider bytes"}))
