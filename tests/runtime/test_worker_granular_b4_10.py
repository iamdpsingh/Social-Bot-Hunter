"""Granular worker test 10."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from sbh.runtime.job import JobPriority
from sbh.runtime.queue import PersistentJobQueue


class TestWorkerGranularB410(unittest.TestCase):
    def test_granular_assertion_10(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            q = PersistentJobQueue(Path(td) / "q_10.sqlite")
            job = q.enqueue("task_10", {"idx": 10}, priority=JobPriority.NORMAL)
            self.assertEqual(job.task_type, "task_10")
            stats = q.get_queue_stats()
            self.assertEqual(stats["queued"], 1)


if __name__ == "__main__":
    unittest.main()
