"""Integration tests for database migration application, failure rollback, and reversibility."""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from sbh.shared.errors import SbhError
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from tests.support import make_db


class MigrationsAndRollbackTests(unittest.TestCase):
    def setUp(self):
        self.db, cleanup = make_db()
        self.addCleanup(cleanup)

    def _get_tables(self) -> set[str]:
        if self.db.dialect == "sqlite":
            rows = self.db.query_all("SELECT name FROM sqlite_master WHERE type = 'table'")
            return {r["name"] for r in rows} - {"sqlite_sequence"}
        curr = self.db.query_one("SELECT current_schema() AS s")
        schema = curr["s"] if curr else "public"
        rows = self.db.query_all(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = :s AND table_type = 'BASE TABLE'",
            {"s": schema},
        )
        return {r["table_name"] for r in rows}

    def test_applied_migrations_can_be_rolled_back_cleanly(self):
        # 1. Verify schema tables exist
        tables = self._get_tables()
        self.assertIn("scan_jobs", tables)
        self.assertIn("platform_accounts", tables)
        self.assertIn("risk_assessments", tables)
        self.assertIn("network_clusters", tables)

        # 2. Execute rollback scripts in reverse order
        rollback_dir = Path(__file__).resolve().parents[2] / "db" / "migrations" / "rollback"
        for rollback_file in sorted(rollback_dir.glob("*.rollback.sql"), reverse=True):
            self.db.run_script(rollback_file.read_text(encoding="utf-8"))

        # 3. Verify all tables (except schema_migrations tracker) are dropped
        remaining = self._get_tables() - {"schema_migrations"}
        self.assertEqual(remaining, set())

    def test_failed_migration_rolls_back_atomically(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            # Create a valid migration first
            (tmp_path / "0001_first.sql").write_text(
                "CREATE TABLE test_table_1 (id TEXT PRIMARY KEY, val TEXT);",
                encoding="utf-8",
            )
            # Create a second migration that succeeds partially then fails
            (tmp_path / "0002_broken.sql").write_text(
                "CREATE TABLE test_table_2 (id TEXT PRIMARY KEY);\n"
                "THIS IS INVALID SQL THAT WILL FAIL;\n",
                encoding="utf-8",
            )

            # Test on fresh clean database
            test_db = SQLiteDatabase()
            self.addCleanup(test_db.close)

            # Applying migrations where 0002 is broken must fail
            with self.assertRaises(sqlite3.OperationalError):
                apply_migrations(test_db, tmp_path)

            tables = {
                r["name"]
                for r in test_db.query_all("SELECT name FROM sqlite_master WHERE type = 'table'")
            }
            # 0001_first succeeded before 0002_broken
            self.assertIn("test_table_1", tables)
            # 0002_broken failed and rolled back cleanly without leaving partial tables
            self.assertNotIn("test_table_2", tables)

            # Ensure schema_migrations records only 0001_first, NOT 0002_broken
            applied = [
                r["version"] for r in test_db.query_all("SELECT version FROM schema_migrations")
            ]
            self.assertEqual(applied, ["0001_first"])

    def test_modified_applied_migration_raises_sbh_error(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            mig_file = tmp_path / "0001_sample.sql"
            mig_file.write_text("CREATE TABLE sample_a (id TEXT PRIMARY KEY);", encoding="utf-8")

            test_db = SQLiteDatabase()
            self.addCleanup(test_db.close)

            apply_migrations(test_db, tmp_path)

            # Modify checksum
            mig_file.write_text(
                "CREATE TABLE sample_a (id TEXT PRIMARY KEY, extra TEXT);", encoding="utf-8"
            )
            with self.assertRaises(SbhError) as ctx:
                apply_migrations(test_db, tmp_path)
            self.assertIn("modified after being applied", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
