"""Bounded-concurrency local background worker loop."""

from __future__ import annotations

import logging
import os
import time
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any

from sbh.runtime.job import Job
from sbh.runtime.queue import PersistentJobQueue
from sbh.runtime.signals import SignalManager

logger = logging.getLogger(__name__)

TaskHandler = Callable[[Job], dict[str, Any]]


class TaskRegistry:
    """Registry mapping task_type string to worker handler functions."""

    def __init__(self) -> None:
        self._handlers: dict[str, TaskHandler] = {}
        self._register_default_tasks()

    def register(self, task_type: str, handler: TaskHandler) -> None:
        self._handlers[task_type] = handler

    def get(self, task_type: str) -> TaskHandler | None:
        return self._handlers.get(task_type)

    def _register_default_tasks(self) -> None:
        """Register built-in system tasks."""

        def _storage_prune_task(job: Job) -> dict[str, Any]:
            from sbh.storage.fs import LocalStorageManager
            from sbh.storage.retention_engine import StorageRetentionEngine

            mgr = LocalStorageManager()
            engine = StorageRetentionEngine(mgr)
            reports = engine.prune_all()
            return {"reports": [r.to_dict() for r in reports]}

        def _db_backup_task(job: Job) -> dict[str, Any]:
            from sbh.storage.backup import DatabaseBackupEngine
            from sbh.storage.fs import LocalStorageManager

            mgr = LocalStorageManager()
            engine = DatabaseBackupEngine(mgr)
            db_p = Path.cwd() / "sbh-dev.sqlite"
            if not db_p.exists():
                return {"status": "skipped", "reason": "default database file not found"}
            _, meta = engine.backup_sqlite(db_p, notes="automated worker backup")
            return {"backup_id": meta.backup_id, "size_bytes": meta.size_bytes}

        self.register("storage.prune", _storage_prune_task)
        self.register("db.backup", _db_backup_task)


class LocalWorker:
    """Worker instance processing tasks from a PersistentJobQueue."""

    def __init__(
        self,
        queue: PersistentJobQueue | None = None,
        registry: TaskRegistry | None = None,
        worker_id: str | None = None,
    ) -> None:
        self.queue = queue or PersistentJobQueue()
        self.registry = registry or TaskRegistry()
        self.worker_id = worker_id or f"worker_{os.getpid()}_{uuid.uuid4().hex[:6]}"
        self.signals = SignalManager.get_instance()

    def run_once(self) -> bool:
        """Attempt to claim and execute one queued job. Returns True if job was processed."""
        # Periodically reclaim stale leases
        self.queue.reclaim_stale_leases()

        job = self.queue.dequeue(self.worker_id)
        if not job:
            return False

        handler = self.registry.get(job.task_type)
        if not handler:
            self.queue.fail_job(job.job_id, f"No handler registered for task_type: {job.task_type}")
            return True

        try:
            result = handler(job)
            self.queue.complete_job(job.job_id, result)
        except Exception as exc:
            logger.exception("Worker %s encountered error executing job %s", self.worker_id, job.job_id)
            self.queue.fail_job(job.job_id, str(exc))

        return True

    def run_loop(self, poll_interval: float = 0.5, max_jobs: int | None = None) -> int:
        """Run continuous worker polling loop until shutdown or job limit."""
        processed = 0
        while not self.signals.is_shutting_down():
            if max_jobs is not None and processed >= max_jobs:
                break

            did_work = self.run_once()
            if did_work:
                processed += 1
            else:
                time.sleep(poll_interval)

        return processed
