from __future__ import annotations

from tests.support import DbTestCase


class StorageSqliteBusyTimeoutTestCase(DbTestCase):
    def test_busy_timeout_query(self) -> None:
        row = self.db.query_one("PRAGMA busy_timeout")
        self.assertIsNotNone(row)
