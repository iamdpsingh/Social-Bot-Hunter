from __future__ import annotations
import unittest
from sbh.pipeline.worker import ScanTask

class PipelineWorkerTest_test_worker_task_lt_comparator(unittest.TestCase):
    def test_lt_not_implemented(self) -> None:
        t = ScanTask(scan_id="s1")
        self.assertEqual(t.__lt__("not_a_task"), NotImplemented)
