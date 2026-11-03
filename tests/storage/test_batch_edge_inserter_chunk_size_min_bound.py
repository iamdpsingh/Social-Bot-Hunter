from __future__ import annotations
import unittest
from sbh.storage.batch import BatchEdgeInserter
from sbh.storage.database import SQLiteDatabase

class StorageBatchTest_test_batch_edge_inserter_chunk_size_min_bound(unittest.TestCase):
    def test_chunk_size_min(self) -> None:
        db = SQLiteDatabase(':memory:')
        inserter = BatchEdgeInserter(db, chunk_size=-10)
        self.assertEqual(inserter.chunk_size, 1)
