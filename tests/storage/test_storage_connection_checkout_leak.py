from __future__ import annotations

from tests.support import DbTestCase


class StorageConnectionCheckoutLeakTestCase(DbTestCase):
    def test_multiple_sequential_queries_keep_connection_healthy(self) -> None:
        for _ in range(50):
            row = self.db.query_one("SELECT 1 AS alive")
            self.assertIsNotNone(row)
            assert row is not None
            self.assertEqual(row["alive"], 1)
