"""Granular worker test 01."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sbh.runtime.job import JobPriority
from sbh.runtime.queue import PersistentJobQueue


class TestWorkerGranularB401(unittest.TestCase):
    def test_granular_assertion_01(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            q = PersistentJobQueue(Path(td) / "q_01.sqlite")
            job = q.enqueue("task_01", {"idx": 1}, priority=JobPriority.NORMAL)
            self.assertEqual(job.task_type, "task_01")
            stats = q.get_queue_stats()
            self.assertEqual(stats["queued"], 1)


if __name__ == "__main__":
    unittest.main()
