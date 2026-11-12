"""Granular worker test 11."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from sbh.runtime.job import JobPriority
from sbh.runtime.queue import PersistentJobQueue


class TestWorkerGranularB411(unittest.TestCase):
    def test_granular_assertion_11(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            q = PersistentJobQueue(Path(td) / "q_11.sqlite")
            job = q.enqueue("task_11", {"idx": 11}, priority=JobPriority.NORMAL)
            self.assertEqual(job.task_type, "task_11")
            stats = q.get_queue_stats()
            self.assertEqual(stats["queued"], 1)


if __name__ == "__main__":
    unittest.main()
