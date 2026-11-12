"""Tests for CLI storage and db commands."""

from __future__ import annotations

import io
import sqlite3
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from sbh.cli import main


class TestStorageCLI(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.base = Path(self.td.name)
        self.db_path = self.base / "cli_test.sqlite"
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("CREATE TABLE test_data (id INT)")
            conn.execute("INSERT INTO test_data VALUES (42)")
            conn.commit()

    def tearDown(self) -> None:
        self.td.cleanup()

    def test_storage_stats_cli(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(["storage-stats", "--json"])
        self.assertEqual(code, 0)
        self.assertIn('"snapshots"', buf.getvalue())

    def test_db_backup_and_verify_cli(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(["db-backup", "--db", str(self.db_path), "--json"])
        self.assertEqual(code, 0)
        self.assertIn('"backup_id"', buf.getvalue())

        # Verify db file directly
        buf_v = io.StringIO()
        with redirect_stdout(buf_v):
            code_v = main(["db-verify", str(self.db_path), "--json"])
        self.assertEqual(code_v, 0)
        self.assertIn('"is_valid": true', buf_v.getvalue())


if __name__ == "__main__":
    unittest.main()
