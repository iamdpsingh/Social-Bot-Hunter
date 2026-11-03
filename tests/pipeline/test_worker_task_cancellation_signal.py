from __future__ import annotations
import unittest
from sbh.pipeline.worker import ScanTask, TaskStatus

class PipelineWorkerTest_test_worker_task_cancellation_signal(unittest.TestCase):
    def test_cancel_sets_flag(self) -> None:
        t = ScanTask(scan_id="s_cancel")
        t.cancel()
        self.assertTrue(t.cancellation_requested.is_set())
        self.assertEqual(t.status, TaskStatus.CANCELLED)
