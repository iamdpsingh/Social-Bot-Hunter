"""Tests for LocalStorageManager and path safety."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sbh.storage.fs import (
    LocalStorageManager,
    StorageCategory,
    compute_sha256,
)


class TestLocalStorageManager(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.mgr = LocalStorageManager(Path(self.td.name))

    def tearDown(self) -> None:
        self.td.cleanup()

    def test_ensure_all_dirs(self) -> None:
        dirs = self.mgr.ensure_all_dirs()
        self.assertIn("snapshots", dirs)
        self.assertIn("models", dirs)
        self.assertTrue(dirs["snapshots"].is_dir())

    def test_safe_resolve_success(self) -> None:
        p = self.mgr.safe_resolve(StorageCategory.SNAPSHOTS, "snap_01.csv")
        self.assertEqual(p.name, "snap_01.csv")

    def test_safe_resolve_traversal_detection(self) -> None:
        with self.assertRaises(ValueError):
            self.mgr.safe_resolve(StorageCategory.SNAPSHOTS, "../../etc/passwd")

    def test_atomic_write_and_sha256(self) -> None:
        target, digest, size = self.mgr.atomic_write(
            StorageCategory.MODELS, "test_model.bin", b"binary content payload"
        )
        self.assertTrue(target.exists())
        self.assertEqual(size, len(b"binary content payload"))
        self.assertEqual(digest, compute_sha256(target))

    def test_directory_stats(self) -> None:
        self.mgr.atomic_write(StorageCategory.EXPORTS, "exp1.json", b"{}")
        self.mgr.atomic_write(StorageCategory.EXPORTS, "exp2.json", b"{}")
        stats = self.mgr.get_directory_stats(StorageCategory.EXPORTS)
        self.assertEqual(stats.file_count, 2)
        self.assertGreater(stats.total_bytes, 0)

    def test_list_and_delete_asset(self) -> None:
        self.mgr.atomic_write(StorageCategory.TEMP, "temp.log", "hello")
        assets = self.mgr.list_assets(StorageCategory.TEMP)
        self.assertEqual(len(assets), 1)
        self.assertEqual(assets[0].filename, "temp.log")

        deleted = self.mgr.delete_asset(StorageCategory.TEMP, "temp.log")
        self.assertTrue(deleted)
        self.assertEqual(len(self.mgr.list_assets(StorageCategory.TEMP)), 0)


if __name__ == "__main__":
    unittest.main()
