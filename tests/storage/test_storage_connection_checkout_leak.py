from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageConnectionCheckoutLeakTestCase(DbTestCase):
    def test_multiple_sequential_queries_keep_connection_healthy(self):
        for _ in range(50):
            row = self.db.query_one("SELECT 1 AS alive")
            self.assertEqual(row["alive"], 1)
