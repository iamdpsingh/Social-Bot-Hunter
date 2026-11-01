from __future__ import annotations

from tests.support import DbTestCase


class StorageSqliteWalModeTestCase(DbTestCase):
    def test_in_memory_engine_journal_mode(self) -> None:
        row = self.db.query_one("PRAGMA journal_mode")
        self.assertIsNotNone(row)
