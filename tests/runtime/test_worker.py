"""Tests for LocalWorker task execution loop."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sbh.runtime.job import Job, JobStatus
from sbh.runtime.queue import PersistentJobQueue
from sbh.runtime.worker import LocalWorker, TaskRegistry


class TestLocalWorker(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.db_path = Path(self.td.name) / "worker_test.sqlite"
        self.queue = PersistentJobQueue(self.db_path)
        self.registry = TaskRegistry()
        self.worker = LocalWorker(self.queue, self.registry)

    def tearDown(self) -> None:
        self.td.cleanup()

    def test_worker_executes_registered_task(self) -> None:
        def my_task(job: Job) -> dict[str, str]:
            return {"greeting": f"Hello {job.payload.get('name')}"}

        self.registry.register("greet", my_task)
        job = self.queue.enqueue("greet", {"name": "BotHunter"})

        did_work = self.worker.run_once()
        self.assertTrue(did_work)

        fetched = self.queue.get_job(job.job_id)
        assert fetched is not None
        self.assertEqual(fetched.status, JobStatus.COMPLETED.value)
        self.assertEqual(fetched.result_data, {"greeting": "Hello BotHunter"})

    def test_worker_handles_task_exception(self) -> None:
        def failing_task(job: Job) -> dict[str, str]:
            raise ValueError("Deliberate failure")

        self.registry.register("fail", failing_task)
        job = self.queue.enqueue("fail", max_attempts=1)

        self.worker.run_once()
        fetched = self.queue.get_job(job.job_id)
        assert fetched is not None
        self.assertEqual(fetched.status, JobStatus.DEAD_LETTER.value)
        self.assertIn("Deliberate failure", fetched.error_message or "")


if __name__ == "__main__":
    unittest.main()
