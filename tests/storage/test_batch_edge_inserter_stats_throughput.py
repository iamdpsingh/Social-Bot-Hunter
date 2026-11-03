from __future__ import annotations
import unittest
from sbh.storage.batch import BatchInsertStats

class StorageBatchTest_test_batch_edge_inserter_stats_throughput(unittest.TestCase):
    def test_throughput_calc(self) -> None:
        stats = BatchInsertStats(total_records=1000, chunks_executed=1, duration_seconds=0.1, throughput_records_per_sec=10000.0)
        self.assertEqual(stats.throughput_records_per_sec, 10000.0)
