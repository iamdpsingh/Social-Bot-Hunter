"""Tests for StorageRetentionEngine and LRU pruning."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sbh.storage.fs import LocalStorageManager, StorageCategory
from sbh.storage.manifest import AssetManifestManager
from sbh.storage.retention_engine import (
    RetentionPolicy,
    StorageRetentionEngine,
)


class TestStorageRetentionEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.storage = LocalStorageManager(Path(self.td.name))
        self.manifest = AssetManifestManager(self.storage)
        self.engine = StorageRetentionEngine(self.storage, self.manifest)

    def tearDown(self) -> None:
        self.td.cleanup()

    def test_keep_minimum_count(self) -> None:
        for i in range(5):
            self.storage.atomic_write(
                StorageCategory.EXPORTS, f"exp_{i}.json", f'{{"id": {i}}}'
            )
        pol = RetentionPolicy(max_age_days=0, keep_minimum_count=3)
        rep = self.engine.prune_category(StorageCategory.EXPORTS, pol)
        self.assertEqual(rep.deleted_count, 2)
        self.assertEqual(rep.preserved_count, 3)

    def test_protected_asset_preserved(self) -> None:
        # Create 6 models
        for i in range(6):
            self.storage.atomic_write(
                StorageCategory.MODELS, f"model_{i}.bin", b"bytes" * 100
            )
            # Mark model_0 as protected
            if i == 0:
                self.manifest.register_asset(
                    StorageCategory.MODELS, f"model_{i}.bin", is_protected=True
                )

        pol = RetentionPolicy(max_age_days=0, keep_minimum_count=1)
        rep = self.engine.prune_category(StorageCategory.MODELS, pol)
        self.assertNotIn("model_0.bin", rep.deleted_files)

    def test_dry_run_mode(self) -> None:
        for i in range(5):
            self.storage.atomic_write(
                StorageCategory.TEMP, f"temp_{i}.tmp", b"temp"
            )
        pol = RetentionPolicy(max_age_days=0, keep_minimum_count=1)
        rep = self.engine.prune_category(StorageCategory.TEMP, pol, dry_run=True)
        self.assertTrue(rep.dry_run)
        self.assertEqual(rep.deleted_count, 4)
        # Verify files still exist on disk
        assets = self.storage.list_assets(StorageCategory.TEMP)
        self.assertEqual(len(assets), 5)


if __name__ == "__main__":
    unittest.main()
