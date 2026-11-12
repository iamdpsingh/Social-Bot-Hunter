"""Tests for PersistentJobQueue priority scheduling and retry mechanics."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sbh.runtime.job import JobPriority, JobStatus
from sbh.runtime.queue import PersistentJobQueue


class TestPersistentJobQueue(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.db_path = Path(self.td.name) / "test_queue.sqlite"
        self.queue = PersistentJobQueue(self.db_path)

    def tearDown(self) -> None:
        self.td.cleanup()

    def test_enqueue_and_dequeue_priority(self) -> None:
        self.queue.enqueue("low_task", priority=JobPriority.LOW)
        self.queue.enqueue("crit_task", priority=JobPriority.CRITICAL)
        self.queue.enqueue("norm_task", priority=JobPriority.NORMAL)

        claimed = self.queue.dequeue("worker_1")
        self.assertIsNotNone(claimed)
        assert claimed is not None
        self.assertEqual(claimed.task_type, "crit_task")

        claimed2 = self.queue.dequeue("worker_1")
        self.assertIsNotNone(claimed2)
        assert claimed2 is not None
        self.assertEqual(claimed2.task_type, "norm_task")

    def test_complete_job(self) -> None:
        job = self.queue.enqueue("simple")
        claimed = self.queue.dequeue("worker_1")
        assert claimed is not None
        ok = self.queue.complete_job(claimed.job_id, {"msg": "done"})
        self.assertTrue(ok)

        fetched = self.queue.get_job(job.job_id)
        assert fetched is not None
        self.assertEqual(fetched.status, JobStatus.COMPLETED.value)
        self.assertEqual(fetched.result_data, {"msg": "done"})

    def test_fail_and_dead_letter(self) -> None:
        job = self.queue.enqueue("flaky", max_attempts=2)

        # Attempt 1
        claimed = self.queue.dequeue("worker_1")
        assert claimed is not None
        self.queue.fail_job(claimed.job_id, "fail 1")
        fetched = self.queue.get_job(job.job_id)
        assert fetched is not None
        self.assertEqual(fetched.status, JobStatus.QUEUED.value)

        # Attempt 2 -> moves to dead letter
        claimed2 = self.queue.dequeue("worker_1")
        assert claimed2 is not None
        self.queue.fail_job(claimed2.job_id, "fail 2")
        fetched2 = self.queue.get_job(job.job_id)
        assert fetched2 is not None
        self.assertEqual(fetched2.status, JobStatus.DEAD_LETTER.value)

    def test_queue_stats(self) -> None:
        self.queue.enqueue("task_1")
        self.queue.enqueue("task_2")
        stats = self.queue.get_queue_stats()
        self.assertEqual(stats["queued"], 2)


if __name__ == "__main__":
    unittest.main()
