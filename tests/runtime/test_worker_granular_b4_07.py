"""Granular worker test 07."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sbh.runtime.job import JobPriority
from sbh.runtime.queue import PersistentJobQueue


class TestWorkerGranularB407(unittest.TestCase):
    def test_granular_assertion_07(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            q = PersistentJobQueue(Path(td) / "q_07.sqlite")
            job = q.enqueue("task_07", {"idx": 7}, priority=JobPriority.NORMAL)
            self.assertEqual(job.task_type, "task_07")
            stats = q.get_queue_stats()
            self.assertEqual(stats["queued"], 1)


if __name__ == "__main__":
    unittest.main()
