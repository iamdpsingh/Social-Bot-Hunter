from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StoragePostgresReconnectTestCase(DbTestCase):
    def test_reconnect_resilience(self):
        row1 = self.db.query_one("SELECT 1 AS val")
        self.assertEqual(row1["val"], 1)
