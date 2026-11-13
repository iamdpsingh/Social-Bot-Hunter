"""Tests verifying directory traversal and archive expansion boundaries."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sbh.storage.fs import LocalStorageManager, StorageCategory


class TestTraversalDefense(unittest.TestCase):
    def test_path_traversal_parent_escape_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            mgr = LocalStorageManager(base_dir=Path(td))
            with self.assertRaises(ValueError):
                mgr.safe_resolve(StorageCategory.EXPORTS, "../../../../etc/passwd")

    def test_path_traversal_absolute_escape_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            mgr = LocalStorageManager(base_dir=Path(td))
            with self.assertRaises(ValueError):
                mgr.safe_resolve(StorageCategory.SNAPSHOTS, "/var/run/secret")


if __name__ == "__main__":
    unittest.main()
