"""Tests for DatabaseBackupEngine and atomic SQLite snapshots."""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from sbh.storage.backup import DatabaseBackupEngine
from sbh.storage.fs import LocalStorageManager


class TestDatabaseBackupEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.base = Path(self.td.name)
        self.storage = LocalStorageManager(self.base)
        self.engine = DatabaseBackupEngine(self.storage)

        # Create sample sqlite DB
        self.db_path = self.base / "test_app.sqlite"
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
            conn.execute("INSERT INTO users (name) VALUES ('Alice'), ('Bob')")
            conn.commit()

    def tearDown(self) -> None:
        self.td.cleanup()

    def test_backup_sqlite_uncompressed(self) -> None:
        bak_path, meta = self.engine.backup_sqlite(self.db_path, compress=False)
        self.assertTrue(bak_path.exists())
        self.assertEqual(meta.table_counts.get("users"), 2)
        self.assertFalse(meta.is_compressed)
        self.assertEqual(len(meta.sha256), 64)

    def test_backup_sqlite_compressed(self) -> None:
        bak_path, meta = self.engine.backup_sqlite(self.db_path, compress=True)
        self.assertTrue(bak_path.exists())
        self.assertTrue(meta.is_compressed)
        self.assertTrue(bak_path.name.endswith(".gz"))

    def test_list_and_delete_backups(self) -> None:
        _, meta = self.engine.backup_sqlite(self.db_path)
        backups = self.engine.list_backups()
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].backup_id, meta.backup_id)

        deleted = self.engine.delete_backup(meta.backup_id)
        self.assertTrue(deleted)
        self.assertEqual(len(self.engine.list_backups()), 0)


if __name__ == "__main__":
    unittest.main()
