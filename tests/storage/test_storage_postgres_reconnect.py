from __future__ import annotations

from tests.support import DbTestCase


class StoragePostgresReconnectTestCase(DbTestCase):
    def test_reconnect_resilience(self) -> None:
        row1 = self.db.query_one("SELECT 1 AS val")
        self.assertIsNotNone(row1)
        assert row1 is not None
        self.assertEqual(row1["val"], 1)
