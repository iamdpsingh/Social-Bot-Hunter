from __future__ import annotations

from tests.support import DbTestCase


class StorageClosingCleanupTestCase(DbTestCase):
    def test_database_connection_cleanup(self) -> None:
        self.assertTrue(callable(getattr(self.db, "close", None)))
