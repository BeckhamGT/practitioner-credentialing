"""Preparation preserves reviewed bytes and excludes other batch readings."""

import json
import tempfile
import unittest
from pathlib import Path

from tools.prepare_batch import prepare
from credentialing.validation import digest


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.archive = self.root / "archive.json";self.manifest = self.root / "manifest.json"
        self.data = {"readings": [{"batch": 1, "id": "synthetic-1", "path": "batch-01/data.csv", "content": "earlier\n", "url": "https://example.org/1"},
                                  {"batch": 2, "id": "synthetic-2", "path": "batch-02/data.csv", "content": "future\n", "url": "https://example.org/2"}]}
        self.contract = {"batch": 1, "files": [{"path": "data.csv", "source_id": "synthetic-1", "source_batch": 1,
                                              "sha256": digest(b"earlier\n"), "source_url": "https://example.org/1"}]}
        self.save()

    def save(self):
        self.archive.write_text(json.dumps(self.data));self.manifest.write_text(json.dumps(self.contract))

    def test_only_selected_batch_bytes_and_exact_manifest_are_materialized(self):
        dest = self.root / "inputs"
        self.assertEqual(prepare(self.archive, self.manifest, dest), "prepared")
        self.assertEqual((dest / "data.csv").read_bytes(), b"earlier\n")
        self.assertEqual((dest / "input.manifest.json").read_bytes(), self.manifest.read_bytes())
        self.assertEqual(prepare(self.archive, self.manifest, dest), "unchanged")

    def test_mixed_batch_hash_or_provenance_failure_leaves_no_output(self):
        self.contract["files"][0]["source_batch"] = 2;self.save()
        with self.assertRaises(ValueError):prepare(self.archive, self.manifest, self.root / "bad")
        self.assertFalse((self.root / "bad").exists())

    def test_existing_different_source_is_preserved(self):
        dest = self.root / "inputs";prepare(self.archive, self.manifest, dest)
        (dest / "data.csv").write_bytes(b"existing work")
        with self.assertRaises(ValueError):prepare(self.archive, self.manifest, dest)
        self.assertEqual((dest / "data.csv").read_bytes(), b"existing work")

    def test_traversal_is_rejected_before_output_creation(self):
        self.contract["files"][0]["path"] = "../escape";self.save()
        with self.assertRaises(ValueError):prepare(self.archive, self.manifest, self.root / "bad")
        self.assertFalse((self.root / "bad").exists())
