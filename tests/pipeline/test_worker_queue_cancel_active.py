from __future__ import annotations
import unittest
from sbh.pipeline.worker import BoundedJobQueue, ScanTask, TaskStatus

class PipelineWorkerTest_test_worker_queue_cancel_active(unittest.TestCase):
    def test_cancel_in_queue(self) -> None:
        q = BoundedJobQueue(maxsize=10)
        q.submit(ScanTask(scan_id="s_active"))
        self.assertTrue(q.cancel("s_active"))
        task = q.get_task("s_active")
        self.assertIsNotNone(task)
        assert task is not None
        self.assertEqual(task.status, TaskStatus.CANCELLED)
