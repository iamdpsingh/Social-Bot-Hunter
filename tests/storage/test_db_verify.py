"""Tests for SQLite database and backup integrity verification."""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from sbh.storage.backup import DatabaseBackupEngine
from sbh.storage.db_verify import verify_backup_integrity, verify_sqlite_database
from sbh.storage.fs import LocalStorageManager


class TestDatabaseVerify(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.base = Path(self.td.name)
        self.db_path = self.base / "good.sqlite"
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("CREATE TABLE items (id INT, val TEXT)")
            conn.execute("INSERT INTO items VALUES (1, 'ok')")
            conn.commit()

    def tearDown(self) -> None:
        self.td.cleanup()

    def test_verify_valid_sqlite_db(self) -> None:
        rep = verify_sqlite_database(self.db_path)
        self.assertTrue(rep.is_valid)
        self.assertTrue(rep.integrity_check_passed)
        self.assertTrue(rep.foreign_keys_valid)
        self.assertIn("items", rep.tables)

    def test_verify_corrupt_sqlite_db(self) -> None:
        corrupt = self.base / "corrupt.sqlite"
        corrupt.write_bytes(b"NOT AN SQLITE DATABASE FILE")
        rep = verify_sqlite_database(corrupt)
        self.assertFalse(rep.is_valid)
        self.assertIn("Invalid SQLite magic header", rep.errors)

    def test_verify_backup_integrity(self) -> None:
        mgr = LocalStorageManager(self.base)
        engine = DatabaseBackupEngine(mgr)
        bak_path, meta = engine.backup_sqlite(self.db_path)

        ok, msg = verify_backup_integrity(bak_path)
        self.assertTrue(ok)
        self.assertIn("verified successfully", msg)


if __name__ == "__main__":
    unittest.main()
