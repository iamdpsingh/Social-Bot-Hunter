from __future__ import annotations
import unittest
from sbh.pipeline.worker import TaskStatus

class PipelineWorkerTest_test_worker_task_status_lifecycle(unittest.TestCase):
    def test_enum_values(self) -> None:
        self.assertEqual(TaskStatus.QUEUED.value, "queued")
        self.assertEqual(TaskStatus.RUNNING.value, "running")
        self.assertEqual(TaskStatus.SUCCEEDED.value, "succeeded")
        self.assertEqual(TaskStatus.FAILED.value, "failed")
        self.assertEqual(TaskStatus.CANCELLED.value, "cancelled")
