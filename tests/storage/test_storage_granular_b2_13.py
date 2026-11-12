"""Granular storage engine test 13."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from sbh.storage.fs import LocalStorageManager, StorageCategory


class TestStorageGranularB213(unittest.TestCase):
    def test_granular_assertion_13(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            mgr = LocalStorageManager(Path(td))
            p, d, sz = mgr.atomic_write(StorageCategory.TEMP, "f_13.dat", b"val_13")
            self.assertTrue(p.exists())
            self.assertGreater(sz, 0)
            self.assertEqual(len(d), 64)


if __name__ == "__main__":
    unittest.main()
