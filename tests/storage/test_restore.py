"""Tests for DatabaseRestoreEngine and safe atomic swaps."""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from sbh.storage.backup import DatabaseBackupEngine
from sbh.storage.fs import LocalStorageManager
from sbh.storage.restore import DatabaseRestoreEngine


class TestDatabaseRestoreEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.base = Path(self.td.name)
        self.storage = LocalStorageManager(self.base)
        self.backup_engine = DatabaseBackupEngine(self.storage)
        self.restore_engine = DatabaseRestoreEngine(self.storage)

        # Source DB with 10 rows
        self.source_db = self.base / "source.sqlite"
        with sqlite3.connect(str(self.source_db)) as conn:
            conn.execute("CREATE TABLE logs (msg TEXT)")
            for i in range(10):
                conn.execute("INSERT INTO logs VALUES (?)", (f"msg_{i}",))
            conn.commit()

        # Target DB with 2 rows
        self.target_db = self.base / "target.sqlite"
        with sqlite3.connect(str(self.target_db)) as conn:
            conn.execute("CREATE TABLE logs (msg TEXT)")
            conn.execute("INSERT INTO logs VALUES ('old1'), ('old2')")
            conn.commit()

    def tearDown(self) -> None:
        self.td.cleanup()

    def test_restore_uncompressed_sqlite(self) -> None:
        bak_path, _ = self.backup_engine.backup_sqlite(self.source_db)
        res = self.restore_engine.restore_sqlite(bak_path, self.target_db)
        self.assertTrue(res.success)
        self.assertIsNotNone(res.safety_backup_path)

        # Verify target DB now has 10 rows
        with sqlite3.connect(str(self.target_db)) as conn:
            count = conn.execute("SELECT COUNT(*) FROM logs").fetchone()[0]
            self.assertEqual(count, 10)

    def test_restore_compressed_sqlite(self) -> None:
        bak_path, _ = self.backup_engine.backup_sqlite(self.source_db, compress=True)
        res = self.restore_engine.restore_sqlite(bak_path, self.target_db)
        self.assertTrue(res.success)

        with sqlite3.connect(str(self.target_db)) as conn:
            count = conn.execute("SELECT COUNT(*) FROM logs").fetchone()[0]
            self.assertEqual(count, 10)


if __name__ == "__main__":
    unittest.main()
