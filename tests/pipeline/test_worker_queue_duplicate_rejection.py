from __future__ import annotations
import unittest
from sbh.pipeline.worker import BoundedJobQueue, ScanTask

class PipelineWorkerTest_test_worker_queue_duplicate_rejection(unittest.TestCase):
    def test_duplicate_rejected(self) -> None:
        q = BoundedJobQueue(maxsize=10)
        self.assertTrue(q.submit(ScanTask(scan_id="s_dup")))
        self.assertFalse(q.submit(ScanTask(scan_id="s_dup")))
