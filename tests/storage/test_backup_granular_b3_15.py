"""Granular database backup and verify test 15."""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path
from sbh.storage.backup import DatabaseBackupEngine
from sbh.storage.fs import LocalStorageManager


class TestBackupGranularB315(unittest.TestCase):
    def test_granular_assertion_15(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            mgr = LocalStorageManager(base)
            eng = DatabaseBackupEngine(mgr)
            db_p = base / "db_15.sqlite"
            with sqlite3.connect(str(db_p)) as conn:
                conn.execute("CREATE TABLE t_15 (x INT)")
                conn.execute("INSERT INTO t_15 VALUES (15)")
                conn.commit()
            bak_p, meta = eng.backup_sqlite(db_p)
            self.assertTrue(bak_p.exists())
            self.assertEqual(meta.table_counts.get("t_15"), 1)


if __name__ == "__main__":
    unittest.main()
