from __future__ import annotations

from tests.support import DbTestCase


class StorageConnectionPingTestCase(DbTestCase):
    def test_database_ping_query(self) -> None:
        row = self.db.query_one("SELECT 1 AS ok")
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["ok"], 1)
