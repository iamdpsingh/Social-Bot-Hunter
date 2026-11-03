from __future__ import annotations
import unittest
from sbh.storage.batch import BatchEdgeInserter
from sbh.storage.database import SQLiteDatabase

class StorageBatchTest_test_batch_edge_inserter_custom_chunk_size(unittest.TestCase):
    def test_chunk_size_setting(self) -> None:
        db = SQLiteDatabase(':memory:')
        inserter = BatchEdgeInserter(db, chunk_size=500)
        self.assertEqual(inserter.chunk_size, 500)
