from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageSqliteBusyTimeoutTestCase(DbTestCase):
    def test_busy_timeout_query(self):
        row = self.db.query_one("PRAGMA busy_timeout")
        self.assertIsNotNone(row)
