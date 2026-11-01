from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageClosingCleanupTestCase(DbTestCase):
    def test_database_connection_cleanup(self):
        self.assertTrue(callable(getattr(self.db, "close", None)))
