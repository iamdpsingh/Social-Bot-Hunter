from __future__ import annotations

import unittest

from sbh.pipeline.worker import BoundedJobQueue, ScanTask


class PipelineWorkerTest_test_worker_bounded_queue_capacity(unittest.TestCase):
    def test_queue_overflow_rejection(self) -> None:
        q = BoundedJobQueue(maxsize=2)
        self.assertTrue(q.submit(ScanTask(scan_id="s1")))
        self.assertTrue(q.submit(ScanTask(scan_id="s2")))
        self.assertFalse(q.submit(ScanTask(scan_id="s3")))
        self.assertEqual(q.size(), 2)
