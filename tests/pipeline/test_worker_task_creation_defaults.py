from __future__ import annotations

import unittest

from sbh.pipeline.worker import ScanTask, TaskPriority, TaskStatus


class PipelineWorkerTest_test_worker_task_creation_defaults(unittest.TestCase):
    def test_defaults(self) -> None:
        t = ScanTask(scan_id="s_default")
        self.assertEqual(t.priority, TaskPriority.NORMAL)
        self.assertEqual(t.status, TaskStatus.QUEUED)
        self.assertEqual(t.retry_count, 0)
        self.assertEqual(t.max_retries, 3)
        self.assertFalse(t.cancellation_requested.is_set())
