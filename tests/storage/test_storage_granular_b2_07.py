"""Granular storage engine test 07."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sbh.storage.fs import LocalStorageManager, StorageCategory


class TestStorageGranularB207(unittest.TestCase):
    def test_granular_assertion_07(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            mgr = LocalStorageManager(Path(td))
            p, d, sz = mgr.atomic_write(StorageCategory.TEMP, "f_07.dat", b"val_07")
            self.assertTrue(p.exists())
            self.assertGreater(sz, 0)
            self.assertEqual(len(d), 64)


if __name__ == "__main__":
    unittest.main()
