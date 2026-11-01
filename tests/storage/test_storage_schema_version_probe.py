from __future__ import annotations

from tests.support import DbTestCase


class StorageSchemaVersionProbeTestCase(DbTestCase):
    def test_schema_migrations_table_exists(self) -> None:
        rows = self.db.query_all("SELECT version FROM schema_migrations ORDER BY version")
        versions = [r["version"] for r in rows]
        self.assertIn("0001_init", versions)
        self.assertIn("0002_auth", versions)
