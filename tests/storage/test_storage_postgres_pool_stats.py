from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StoragePostgresPoolStatsTestCase(DbTestCase):
    def test_pool_compatibility(self):
        self.assertTrue(hasattr(self.db, "execute"))
        self.assertTrue(hasattr(self.db, "query"))
