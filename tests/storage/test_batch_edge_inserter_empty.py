from __future__ import annotations

import unittest

from sbh.storage.batch import BatchEdgeInserter
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations


class StorageBatchTest_test_batch_edge_inserter_empty(unittest.TestCase):
    def test_empty_insert(self) -> None:
        db = SQLiteDatabase(":memory:")
        apply_migrations(db)
        inserter = BatchEdgeInserter(db)
        stats = inserter.insert_edges_chunked("s1", [])
        self.assertEqual(stats.total_records, 0)
        self.assertEqual(stats.chunks_executed, 0)
