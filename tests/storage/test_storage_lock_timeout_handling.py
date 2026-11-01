from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageLockTimeoutHandlingTestCase(DbTestCase):
    def test_database_is_usable(self):
        row = self.db.query_one("SELECT 100 AS num")
        self.assertEqual(row["num"], 100)
