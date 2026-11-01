from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageConnectionPingTestCase(DbTestCase):
    def test_database_ping_query(self):
        row = self.db.query_one("SELECT 1 AS ok")
        self.assertEqual(row["ok"], 1)
