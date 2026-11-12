"""Tests for AssetManifestManager and tamper detection."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sbh.storage.fs import LocalStorageManager, StorageCategory
from sbh.storage.manifest import AssetManifestManager


class TestAssetManifestManager(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.storage = LocalStorageManager(Path(self.td.name))
        self.manifest = AssetManifestManager(self.storage)

    def tearDown(self) -> None:
        self.td.cleanup()

    def test_register_and_get_asset(self) -> None:
        self.storage.atomic_write(StorageCategory.MODELS, "clf_v1.bin", b"weights")
        rec = self.manifest.register_asset(
            StorageCategory.MODELS,
            "clf_v1.bin",
            is_protected=True,
            tags=["production", "baseline"],
        )
        self.assertEqual(rec.filename, "clf_v1.bin")
        self.assertTrue(rec.is_protected)
        self.assertIn("production", rec.tags)

        loaded = self.manifest.get_asset(rec.asset_id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.sha256, rec.sha256)

    def test_tamper_detection(self) -> None:
        target, _, _ = self.storage.atomic_write(
            StorageCategory.SNAPSHOTS, "snap.csv", b"original"
        )
        rec = self.manifest.register_asset(StorageCategory.SNAPSHOTS, "snap.csv")

        # Verify initial state matches
        ok, msg = self.manifest.verify_tamper(rec.asset_id)
        self.assertTrue(ok)
        self.assertEqual(msg, "Integrity verified")

        # Tamper with file
        target.write_bytes(b"tampered data modification")
        ok, msg = self.manifest.verify_tamper(rec.asset_id)
        self.assertFalse(ok)
        self.assertIn("Checksum mismatch", msg)


if __name__ == "__main__":
    unittest.main()
