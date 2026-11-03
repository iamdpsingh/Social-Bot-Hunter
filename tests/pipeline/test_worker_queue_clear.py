from __future__ import annotations

import unittest

from sbh.pipeline.worker import BoundedJobQueue, ScanTask


class PipelineWorkerTest_test_worker_queue_clear(unittest.TestCase):
    def test_clear_empties_all(self) -> None:
        q = BoundedJobQueue(maxsize=10)
        q.submit(ScanTask(scan_id="s1"))
        q.submit(ScanTask(scan_id="s2"))
        q.clear()
        self.assertEqual(q.size(), 0)
        self.assertIsNone(q.get_task("s1"))
