from __future__ import annotations

from tests.support import DbTestCase


class StorageLockTimeoutHandlingTestCase(DbTestCase):
    def test_database_is_usable(self) -> None:
        row = self.db.query_one("SELECT 100 AS num")
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["num"], 100)
