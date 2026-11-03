from __future__ import annotations
import unittest
from sbh.storage.batch import BatchEdgeInserter
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations

class StorageBatchTest_test_batch_edge_inserter_stats_duration(unittest.TestCase):
    def test_stats_fields(self) -> None:
        db = SQLiteDatabase(':memory:')
        apply_migrations(db)
        inserter = BatchEdgeInserter(db)
        stats = inserter.insert_edges_chunked('s1', [])
        self.assertGreaterEqual(stats.duration_seconds, 0.0)
        self.assertGreaterEqual(stats.throughput_records_per_sec, 0.0)
