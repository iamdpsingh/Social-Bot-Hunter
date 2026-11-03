from __future__ import annotations

import unittest

from sbh.pipeline.worker import ScanTask, TaskPriority


class PipelineWorkerTest_test_worker_task_priority_ordering(unittest.TestCase):
    def test_priority_order(self) -> None:
        t_high = ScanTask(scan_id="s1", priority=TaskPriority.HIGH)
        t_low = ScanTask(scan_id="s2", priority=TaskPriority.LOW)
        self.assertTrue(t_high < t_low)
