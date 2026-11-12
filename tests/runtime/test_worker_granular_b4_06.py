"""Granular worker test 06."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from sbh.runtime.job import JobPriority
from sbh.runtime.queue import PersistentJobQueue


class TestWorkerGranularB406(unittest.TestCase):
    def test_granular_assertion_06(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            q = PersistentJobQueue(Path(td) / "q_06.sqlite")
            job = q.enqueue("task_06", {"idx": 6}, priority=JobPriority.NORMAL)
            self.assertEqual(job.task_type, "task_06")
            stats = q.get_queue_stats()
            self.assertEqual(stats["queued"], 1)


if __name__ == "__main__":
    unittest.main()
