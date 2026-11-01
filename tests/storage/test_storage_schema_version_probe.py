from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageSchemaVersionProbeTestCase(DbTestCase):
    def test_schema_migrations_table_exists(self):
        rows = self.db.query("SELECT name FROM schema_migrations ORDER BY name")
        names = [r["name"] for r in rows]
        self.assertIn("0001_init", names)
        self.assertIn("0002_auth", names)
