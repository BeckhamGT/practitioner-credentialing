"""Behavioral tests use synthetic evidence, never supplied case outcomes."""

import copy
import csv
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from credentialing.cli import main
from credentialing.storage import Store
from credentialing.validation import (GroundworkError, LAYOUT, digest, json_bytes,
                                      load_batch, read_json)


def csv_bytes(name, rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=LAYOUT[name].split(","), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def fixture(root, batch=1, as_of="2026-03-16", document=False):
    root.mkdir(parents=True)
    for name in LAYOUT:
        (root / name).write_bytes(csv_bytes(name, []))
    (root / "README.md").write_text(f"# Batch {batch} export — synthetic fixture\n\n**Export date: {as_of}**\n")
    # Missing signatures/CV are deliberately preserved as blanks; structural
    # acceptance must never be interpreted as completeness acceptance.
    row = {key: "" for key in LAYOUT["applications.csv"].split(",")}
    row.update(application_id="SYNTH-001", revision="1", received_date=as_of,
               first_received_date=as_of, first_name="Example", last_name="Quoted, Name")
    (root / "applications.csv").write_bytes(csv_bytes("applications.csv", [row]))
    paths = list(LAYOUT) + ["README.md"]
    if document:
        path = "letters/synthetic-note.md"
        (root / "letters").mkdir()
        (root / path).write_text(f"# Synthetic document\n\n**Date:** {as_of}\nNo clinical conclusion.\n")
        (root / "correspondence.csv").write_bytes(csv_bytes("correspondence.csv", [{
            "letter_id": "SYNTH-LETTER", "date": as_of, "direction": "in",
            "application_id": "SYNTH-001", "correspondent": "Example",
            "subject": "Synthetic evidence", "document_path": path,
        }]))
        paths.append(path)
    manifest = {"format": "credentialing-input-manifest/1", "batch": batch, "as_of": as_of,
                "files": [{"path": name, "sha256": digest((root / name).read_bytes()),
                           "source_id": f"synthetic-{batch}-{n}", "source_url": f"https://example.org/synthetic/{batch}/{n}",
                           "source_batch": batch,
                           "kind": "records" if name.endswith(".csv") else "batch-readme" if name == "README.md" else "document"}
                          for n, name in enumerate(paths)]}
    save_manifest(root, manifest)
    return manifest


def save_manifest(root, manifest):
    (root / "input.manifest.json").write_bytes(json_bytes(manifest))


def rehash(root, manifest, name):
    next(f for f in manifest["files"] if f["path"] == name)["sha256"] = digest((root / name).read_bytes())
    save_manifest(root, manifest)


class GroundworkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.input = self.root / "input-1"
        self.manifest = fixture(self.input, document=True)
        self.store = Store(self.root / "state")

    def expect_error(self, code, call):
        with self.assertRaises(GroundworkError) as caught:
            call()
        self.assertEqual(caught.exception.code, code)

    def stage(self, root=None, batch=1, previous=None):
        manifest, raw, contents, _ = load_batch(root or self.input, batch)
        return self.store.stage(manifest, raw, contents, previous)

    def invoke(self, *args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(list(args))
        return code, stdout.getvalue(), stderr.getvalue()

    def test_valid_input_retains_quoted_cells_and_unknowns_without_judgment(self):
        manifest, _, contents, summary = load_batch(self.input, 1)
        row = next(csv.DictReader(io.StringIO(contents["applications.csv"].decode())))
        self.assertEqual(row["last_name"], "Quoted, Name")
        self.assertEqual(row["release_signed_date"], "")
        self.assertEqual(row["cv_received_date"], "")
        self.assertEqual(summary["record_counts"]["applications.csv"], 1)
        self.assertNotIn("applications", manifest)

    def test_header_only_file_is_valid_but_missing_file_is_not(self):
        self.assertEqual(load_batch(self.input, 1)[3]["record_counts"]["peer-referees.csv"], 0)
        (self.input / "peer-referees.csv").unlink()
        self.expect_error("missing_file", lambda: load_batch(self.input, 1))

    def test_source_mutation_is_detected_without_rewriting_it(self):
        path = self.input / "applications.csv"
        changed = path.read_bytes() + b"\n"
        path.write_bytes(changed)
        self.expect_error("hash_mismatch", lambda: load_batch(self.input, 1))
        self.assertEqual(path.read_bytes(), changed)

    def test_wrong_batch_is_rejected_before_source_reads(self):
        read = Path.read_bytes
        reads = []
        def watched(path):
            reads.append(path.name)
            return read(path)
        with patch.object(Path, "read_bytes", watched):
            self.expect_error("wrong_batch", lambda: load_batch(self.input, 2))
        self.assertEqual(reads, ["input.manifest.json"])

    def test_mixed_source_provenance_rejected_before_source_reads(self):
        self.manifest["files"][0]["source_batch"] = 2
        save_manifest(self.input, self.manifest)
        self.expect_error("wrong_batch", lambda: load_batch(self.input, 1))

    def test_unlisted_future_file_is_never_opened(self):
        future = self.input / "future-batch-3-private.md"
        future.write_text("Future evidence must remain unread")
        read = Path.read_bytes
        def guarded(path):
            if path == future:
                raise AssertionError("Future file was read")
            return read(path)
        with patch.object(Path, "read_bytes", guarded):
            self.stage()
        self.assertFalse(any(f["path"] == future.name for f in self.store.current()["state"]["manifest"]["files"]))

    def test_path_escape_and_absolute_paths_are_rejected(self):
        for name in ("../secret", "/tmp/secret", "letters/../secret", "letters//secret", "letters\\secret", "./secret"):
            with self.subTest(name=name):
                manifest = copy.deepcopy(self.manifest)
                manifest["files"][-1]["path"] = name
                save_manifest(self.input, manifest)
                self.expect_error("unsafe_path", lambda: load_batch(self.input, 1))

    def test_symlinked_source_cannot_read_outside_batch(self):
        path = self.input / "letters" / "synthetic-note.md"
        target = self.root / "external.md"
        target.write_bytes(path.read_bytes())
        path.unlink()
        path.symlink_to(target)
        self.expect_error("unsafe_path", lambda: load_batch(self.input, 1))

    def test_duplicate_manifest_paths_and_unknown_json_fields_are_rejected(self):
        self.manifest["files"].append(copy.deepcopy(self.manifest["files"][0]))
        save_manifest(self.input, self.manifest)
        self.expect_error("duplicate_source", lambda: load_batch(self.input, 1))
        self.manifest["files"].pop()
        self.manifest["packet_presentable"] = True
        save_manifest(self.input, self.manifest)
        self.expect_error("invalid_structure", lambda: load_batch(self.input, 1))

    def test_duplicate_json_keys_and_nonfinite_values_are_rejected(self):
        for raw in (b'{"a": 1, "a": 2}', b'{"a": NaN}', b'{"a": Infinity}'):
            with self.subTest(raw=raw):
                self.expect_error("invalid_json", lambda: read_json(raw))

    def test_impossible_export_date_and_boolean_batch_are_rejected(self):
        for key, value in (("as_of", "2026-02-30"), ("batch", True)):
            with self.subTest(key=key):
                manifest = copy.deepcopy(self.manifest)
                manifest[key] = value
                save_manifest(self.input, manifest)
                self.expect_error("invalid_structure", lambda: load_batch(self.input, 1))

    def test_future_observation_rejected_but_future_expiry_is_retained(self):
        path = "licence-lookup-other-states.csv"
        row = {key: "" for key in LAYOUT[path].split(",")}
        row.update(lookup_date="2026-03-16", expiry_date="2027-12-31")
        (self.input / path).write_bytes(csv_bytes(path, [row]))
        rehash(self.input, self.manifest, path)
        load_batch(self.input, 1)
        row["lookup_date"] = "2026-03-17"
        (self.input / path).write_bytes(csv_bytes(path, [row]))
        rehash(self.input, self.manifest, path)
        self.expect_error("future_evidence", lambda: load_batch(self.input, 1))

    def test_future_supporting_document_date_is_rejected(self):
        name = "letters/synthetic-note.md"
        (self.input / name).write_text("# Note\n**Date:** 2026-03-17\n")
        rehash(self.input, self.manifest, name)
        self.expect_error("future_evidence", lambda: load_batch(self.input, 1))

    def test_rehashed_csv_wrong_header_and_row_width_do_not_pass(self):
        path = self.input / "applications.csv"
        original = path.read_bytes()
        path.write_bytes(original.replace(b"application_id,", b"different_id,", 1))
        rehash(self.input, self.manifest, path.name)
        self.expect_error("csv_header", lambda: load_batch(self.input, 1))
        path.write_bytes(original + b"too,few,columns\n")
        rehash(self.input, self.manifest, path.name)
        self.expect_error("csv_width", lambda: load_batch(self.input, 1))

    def test_readme_clock_disagreement_is_rejected(self):
        (self.input / "README.md").write_text("# Batch 1 export\n**Export date: 2026-04-20**\n")
        rehash(self.input, self.manifest, "README.md")
        self.expect_error("batch_readme", lambda: load_batch(self.input, 1))

    def test_invalid_utf8_is_not_cleaned_or_replaced(self):
        name = "letters/synthetic-note.md"
        raw = b"# Invalid UTF-8: \xff\n"
        (self.input / name).write_bytes(raw)
        rehash(self.input, self.manifest, name)
        self.expect_error("invalid_encoding", lambda: load_batch(self.input, 1))
        self.assertEqual((self.input / name).read_bytes(), raw)

    def test_correspondence_reference_cannot_escape_or_omit_document(self):
        path = self.input / "correspondence.csv"
        original = path.read_bytes()
        for replacement, code in ((b"../outside.md", "unsafe_path"), (b"letters/missing.md", "document_index")):
            with self.subTest(code=code):
                path.write_bytes(original.replace(b"letters/synthetic-note.md", replacement))
                rehash(self.input, self.manifest, path.name)
                self.expect_error(code, lambda: load_batch(self.input, 1))

    def test_original_manifest_and_document_bytes_retained_in_state_objects(self):
        receipt = self.stage()
        current = self.store.current()
        self.assertEqual(receipt["state_sha256"], current["sha256"])
        for entry in self.manifest["files"]:
            blob = self.store.root / "objects" / "blobs" / entry["sha256"]
            self.assertEqual(blob.read_bytes(), (self.input / entry["path"]).read_bytes())
        self.assertEqual(current["state"]["business_blockers"], ["G1", "G2"])
        self.assertNotIn("applications", current["state"])
        self.assertNotIn("packet_presentable", current["state"])

    def test_unchanged_rerun_keeps_state_and_head_bytes(self):
        first = self.stage()
        head = (self.store.root / "HEAD.json").read_bytes()
        states = sorted((self.store.root / "objects" / "states").iterdir())
        rerun = self.stage()
        self.assertEqual(rerun["result"], "unchanged")
        self.assertEqual(rerun["state_sha256"], first["state_sha256"])
        self.assertEqual((self.store.root / "HEAD.json").read_bytes(), head)
        self.assertEqual(sorted((self.store.root / "objects" / "states").iterdir()), states)

    def test_changed_retained_batch_is_rejected_without_altering_current(self):
        self.stage()
        head = (self.store.root / "HEAD.json").read_bytes()
        name = "letters/synthetic-note.md"
        (self.input / name).write_bytes((self.input / name).read_bytes() + b"Additional text.\n")
        rehash(self.input, self.manifest, name)
        self.expect_error("changed_batch", self.stage)
        self.assertEqual((self.store.root / "HEAD.json").read_bytes(), head)

    def test_three_synthetic_batches_resume_exact_predecessors(self):
        first = self.stage()["state_sha256"]
        second_path = self.root / "input-2"
        third_path = self.root / "input-3"
        fixture(second_path, 2, "2026-04-20")
        fixture(third_path, 3, "2026-05-18")
        self.expect_error("predecessor_mismatch", lambda: self.stage(second_path, 2))
        second = self.stage(second_path, 2, first)["state_sha256"]
        self.expect_error("predecessor_mismatch", lambda: self.stage(third_path, 3, first))
        third = self.stage(third_path, 3, second)["state_sha256"]
        chain = self.store.current()["chain"]
        self.assertEqual([item[0] for item in chain], [first, second, third])
        self.assertEqual([item[1]["manifest"]["batch"] for item in chain], [1, 2, 3])
        self.assertEqual(self.stage(third_path, 3, second)["result"], "unchanged")

    def test_batch_cannot_start_at_two_or_skip_three(self):
        second_path = self.root / "input-2"
        third_path = self.root / "input-3"
        fixture(second_path, 2, "2026-04-20")
        fixture(third_path, 3, "2026-05-18")
        self.expect_error("batch_sequence", lambda: self.stage(second_path, 2))
        first = self.stage()["state_sha256"]
        self.expect_error("batch_sequence", lambda: self.stage(third_path, 3, first))

    def test_regressing_export_clock_does_not_replace_state(self):
        first = self.stage()["state_sha256"]
        second_path = self.root / "input-2"
        fixture(second_path, 2, "2026-02-01")
        self.expect_error("clock_regression", lambda: self.stage(second_path, 2, first))
        self.assertEqual(self.store.current()["sha256"], first)

    def test_corrupt_predecessor_blob_is_detected_before_advancement(self):
        first = self.stage()["state_sha256"]
        blob = self.store.root / "objects" / "blobs" / self.manifest["files"][0]["sha256"]
        original = blob.read_bytes()
        blob.write_bytes(b"damaged isolated fixture")
        self.expect_error("corrupt_state", self.store.current)
        self.expect_error("corrupt_state", self.stage)
        blob.write_bytes(original)  # Isolated fixture repair, not rewriting supplied evidence.
        self.assertEqual(self.store.current()["sha256"], first)

    def test_corrupt_state_object_and_symlinked_head_are_rejected(self):
        first = self.stage()["state_sha256"]
        state = self.store.root / "objects" / "states" / first
        raw = state.read_bytes()
        state.write_bytes(raw.replace(b'"evidence-only"', b'"complete"'))
        self.expect_error("corrupt_state", self.store.current)
        state.write_bytes(raw)
        head = self.store.root / "HEAD.json"
        other = self.root / "external-head.json"
        other.write_bytes(head.read_bytes())
        head.unlink()
        head.symlink_to(other)
        self.expect_error("unsafe_path", self.store.current)

    def test_missing_head_never_promotes_orphan_or_reinitializes_over_history(self):
        self.stage()
        (self.store.root / "HEAD.json").unlink()
        self.expect_error("missing_state", self.store.current)
        self.expect_error("missing_state", self.stage)

    def test_failed_atomic_pointer_update_preserves_previous_head_and_can_retry(self):
        first = self.stage()["state_sha256"]
        second_path = self.root / "input-2"
        fixture(second_path, 2, "2026-04-20")
        with patch("credentialing.storage.os.replace", side_effect=OSError("isolated write failure")):
            with self.assertRaises(OSError):
                self.stage(second_path, 2, first)
        self.assertEqual(self.store.current()["sha256"], first)
        result = self.stage(second_path, 2, first)
        self.assertEqual(result["batch"], 2)

    def test_unlisted_payload_cannot_be_injected_through_storage_api(self):
        manifest, raw, contents, _ = load_batch(self.input, 1)
        contents["batch-3.txt"] = b"future evidence"
        self.expect_error("source_set", lambda: self.store.stage(manifest, raw, contents, None))
        self.assertFalse((self.store.root / "HEAD.json").exists())

    def test_existing_writer_lock_prevents_state_update(self):
        self.store.root.mkdir()
        (self.store.root / ".write-lock").write_text("isolated synthetic writer")
        self.expect_error("store_busy", self.stage)
        self.assertFalse((self.store.root / "HEAD.json").exists())

    def test_cli_invalid_input_preserves_previous_current_result(self):
        self.stage()
        before = (self.store.root / "HEAD.json").read_bytes()
        path = self.input / "applications.csv"
        path.write_bytes(path.read_bytes() + b"tampered\n")
        code, out, err = self.invoke("stage", "--input", str(self.input), "--batch", "1", "--store", str(self.store.root))
        self.assertEqual(code, 2)
        self.assertFalse(out)
        self.assertEqual(json.loads(err)["error"], "hash_mismatch")
        self.assertEqual((self.store.root / "HEAD.json").read_bytes(), before)

    def test_cli_exits_and_error_receipt_preserve_business_block(self):
        code, out, err = self.invoke("run")
        self.assertEqual(code, 3)
        self.assertFalse(out)
        self.assertEqual(json.loads(err)["error"], "business_blocked")
        self.assertFalse(list(self.root.rglob("batch-01.json")))
        code, out, err = self.invoke("stage", "--input", str(self.input), "--batch", "1", "--store", str(self.store.root))
        self.assertEqual(code, 0, err)
        self.assertFalse(json.loads(out)["assessed_snapshot_written"])
        code, out, err = self.invoke("inspect-state", "--store", str(self.store.root))
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["batches"][0]["batch"], 1)

    def test_cli_rejects_storage_inside_input_and_has_no_network_dependency(self):
        code, _, err = self.invoke("stage", "--input", str(self.input), "--batch", "1", "--store", str(self.input / "state"))
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(err)["error"], "unsafe_path")
        with patch("socket.socket", side_effect=AssertionError("Runtime attempted network")):
            code, out, err = self.invoke("check-input", "--input", str(self.input), "--batch", "1")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["result"], "structure-valid")


if __name__ == "__main__":
    unittest.main()
