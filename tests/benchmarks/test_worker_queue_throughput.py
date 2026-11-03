from __future__ import annotations
import time
import unittest
from sbh.pipeline.worker import BoundedJobQueue, ScanTask

class BenchmarkTest_test_worker_queue_throughput(unittest.TestCase):
    def test_queue_perf(self) -> None:
        q = BoundedJobQueue(maxsize=1000)
        t0 = time.perf_counter()
        for i in range(500):
            q.submit(ScanTask(scan_id=f"s_{i}"))
        duration = time.perf_counter() - t0
        self.assertLess(duration, 0.5)
