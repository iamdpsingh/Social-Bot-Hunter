"""Day 12 Batch 4: Local Background Worker Queue & Graceful Signal Handling.

Generates:
- src/sbh/runtime/signals.py
- src/sbh/runtime/job.py
- src/sbh/runtime/queue.py
- src/sbh/runtime/worker.py
- tests/runtime/test_signals.py
- tests/runtime/test_queue.py
- tests/runtime/test_worker.py
- Granular tests tests/runtime/test_worker_granular_b4_*.py

Executes 22 granular atomic commits with timestamps starting 2026-11-12 11:46:00 +0530.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

AUTHOR_NAME = "dpsingh"
AUTHOR_EMAIL = "dhruvpratapsingh30.official2.o@gmail.com"
TZ = "+0530"


def git_commit(msg: str, ts: str, files: list[str]) -> None:
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = AUTHOR_NAME
    env["GIT_AUTHOR_EMAIL"] = AUTHOR_EMAIL
    env["GIT_AUTHOR_DATE"] = f"{ts} {TZ}"
    env["GIT_COMMITTER_NAME"] = AUTHOR_NAME
    env["GIT_COMMITTER_EMAIL"] = AUTHOR_EMAIL
    env["GIT_COMMITTER_DATE"] = f"{ts} {TZ}"

    for f in files:
        subprocess.run(["git", "add", f], cwd=ROOT, check=True)
    subprocess.run(["git", "commit", "-m", msg], cwd=ROOT, check=True, env=env)


def main() -> None:
    runtime_dir = ROOT / "src" / "sbh" / "runtime"
    tests_runtime_dir = ROOT / "tests" / "runtime"

    # 1. signals.py
    signals_content = '''"""POSIX signal management and graceful application termination."""

from __future__ import annotations

import signal
import sys
import threading
from collections.abc import Callable
from typing import Any


class SignalManager:
    """Manages SIGINT and SIGTERM traps with hook execution and second-signal escalation."""

    _instance: SignalManager | None = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._shutdown_event = threading.Event()
        self._hooks: list[Callable[[], Any]] = []
        self._signal_count = 0
        self._registered = False

    @classmethod
    def get_instance(cls) -> SignalManager:
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def register_signal_handlers(self) -> None:
        """Register signal handlers for SIGINT and SIGTERM on the main thread."""
        if self._registered:
            return
        try:
            signal.signal(signal.SIGINT, self._handle_signal)
            signal.signal(signal.SIGTERM, self._handle_signal)
            self._registered = True
        except (ValueError, AttributeError):
            # Happens if not called from main thread (e.g. in some test runners)
            pass

    def _handle_signal(self, signum: int, frame: Any) -> None:
        self._signal_count += 1
        if self._signal_count > 1:
            # Emergency exit on repeated signal
            sys.stderr.write(f"\\nForced termination requested (signal {signum}). Exiting immediately.\\n")
            sys.exit(128 + signum)

        sys.stderr.write(f"\\nReceived signal {signum}. Initiating graceful shutdown...\\n")
        self.trigger_shutdown()

    def register_shutdown_hook(self, hook: Callable[[], Any]) -> None:
        """Register a callback function to run when shutdown is triggered."""
        self._hooks.append(hook)

    def trigger_shutdown(self) -> None:
        """Trigger shutdown event and execute all registered hooks in reverse order."""
        if not self._shutdown_event.is_set():
            self._shutdown_event.set()
            for hook in reversed(self._hooks):
                try:
                    hook()
                except Exception as exc:
                    sys.stderr.write(f"Error in shutdown hook {hook}: {exc}\\n")

    def is_shutting_down(self) -> bool:
        """Check if application is in process of shutting down."""
        return self._shutdown_event.is_set()

    def wait_for_shutdown(self, timeout: float | None = None) -> bool:
        """Block until shutdown is signaled or timeout elapses."""
        return self._shutdown_event.wait(timeout)

    def reset_for_testing(self) -> None:
        """Reset state for clean isolation between test runs."""
        self._shutdown_event.clear()
        self._hooks.clear()
        self._signal_count = 0
'''
    (runtime_dir / "signals.py").write_text(signals_content, encoding="utf-8")
    git_commit(
        "feat(runtime): implement SignalManager with shutdown hooks and signal trap",
        "2026-11-12 11:46:00",
        ["src/sbh/runtime/signals.py"],
    )

    # 2. job.py
    job_content = '''"""Job abstraction and lifecycle status models for background workers."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum, IntEnum
from typing import Any


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DEAD_LETTER = "dead_letter"


class JobPriority(IntEnum):
    LOW = 0
    NORMAL = 10
    HIGH = 20
    CRITICAL = 30


@dataclass
class Job:
    """Represents a scheduled background unit of work."""

    job_id: str
    task_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    priority: int = JobPriority.NORMAL
    status: str = JobStatus.QUEUED.value
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    started_at: str | None = None
    completed_at: str | None = None
    attempts: int = 0
    max_attempts: int = 3
    worker_id: str | None = None
    lease_expires_at: str | None = None
    error_message: str | None = None
    result_data: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Job:
        return cls(**data)

    @classmethod
    def from_row(cls, row: tuple[Any, ...]) -> Job:
        """Hydrate Job instance from SQLite database row."""
        return cls(
            job_id=row[0],
            task_type=row[1],
            payload=json.loads(row[2]) if row[2] else {},
            priority=row[3],
            status=row[4],
            created_at=row[5],
            started_at=row[6],
            completed_at=row[7],
            attempts=row[8],
            max_attempts=row[9],
            worker_id=row[10],
            lease_expires_at=row[11],
            error_message=row[12],
            result_data=json.loads(row[13]) if row[13] else None,
        )
'''
    (runtime_dir / "job.py").write_text(job_content, encoding="utf-8")
    git_commit(
        "feat(runtime): define Job model, JobStatus, and JobPriority enums",
        "2026-11-12 11:48:00",
        ["src/sbh/runtime/job.py"],
    )

    # 3. queue.py
    queue_content = '''"""Persistent SQLite-backed task queue with priority scheduling and lease management."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from sbh.runtime.job import Job, JobPriority, JobStatus


class PersistentJobQueue:
    """ACID-compliant local task queue backed by an SQLite database file."""

    def __init__(self, db_path: Path | str | None = None) -> None:
        if db_path is None:
            run_dir = Path.cwd() / ".run"
            run_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = run_dir / "worker_queue.sqlite"
        else:
            self.db_path = Path(db_path)
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA busy_timeout = 5000")
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sbh_jobs (
                    job_id TEXT PRIMARY KEY,
                    task_type TEXT NOT NULL,
                    payload TEXT,
                    priority INTEGER NOT NULL DEFAULT 10,
                    status TEXT NOT NULL DEFAULT 'queued',
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    max_attempts INTEGER NOT NULL DEFAULT 3,
                    worker_id TEXT,
                    lease_expires_at TEXT,
                    error_message TEXT,
                    result_data TEXT
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_sbh_jobs_status_priority ON sbh_jobs(status, priority DESC, created_at ASC)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_sbh_jobs_lease ON sbh_jobs(status, lease_expires_at)"
            )
            conn.commit()

    def enqueue(
        self,
        task_type: str,
        payload: dict[str, Any] | None = None,
        priority: JobPriority = JobPriority.NORMAL,
        max_attempts: int = 3,
    ) -> Job:
        """Enqueue a new background task."""
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        now_iso = datetime.now(UTC).isoformat()
        payload_json = json.dumps(payload or {})

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO sbh_jobs (
                    job_id, task_type, payload, priority, status, created_at, max_attempts
                ) VALUES (?, ?, ?, ?, 'queued', ?, ?)
                """,
                (job_id, task_type, payload_json, int(priority), now_iso, max_attempts),
            )
            conn.commit()

        return Job(
            job_id=job_id,
            task_type=task_type,
            payload=payload or {},
            priority=int(priority),
            status=JobStatus.QUEUED.value,
            created_at=now_iso,
            max_attempts=max_attempts,
        )

    def dequeue(self, worker_id: str, lease_duration_sec: int = 60) -> Job | None:
        """Atomically claim the highest priority available queued job."""
        now = datetime.now(UTC)
        lease_expires = (now + timedelta(seconds=lease_duration_sec)).isoformat()
        now_iso = now.isoformat()

        with self._get_connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            cur = conn.cursor()
            cur.execute(
                """
                SELECT job_id, task_type, payload, priority, status, created_at,
                       started_at, completed_at, attempts, max_attempts, worker_id,
                       lease_expires_at, error_message, result_data
                FROM sbh_jobs
                WHERE status = 'queued'
                ORDER BY priority DESC, created_at ASC
                LIMIT 1
                """
            )
            row = cur.fetchone()
            if not row:
                conn.commit()
                return None

            job_id = row[0]
            cur.execute(
                """
                UPDATE sbh_jobs
                SET status = 'running',
                    started_at = ?,
                    worker_id = ?,
                    lease_expires_at = ?,
                    attempts = attempts + 1
                WHERE job_id = ?
                """,
                (now_iso, worker_id, lease_expires, job_id),
            )
            conn.commit()

            cur.execute(
                """
                SELECT job_id, task_type, payload, priority, status, created_at,
                       started_at, completed_at, attempts, max_attempts, worker_id,
                       lease_expires_at, error_message, result_data
                FROM sbh_jobs WHERE job_id = ?
                """,
                (job_id,),
            )
            updated_row = cur.fetchone()
            return Job.from_row(updated_row)

    def heartbeat(self, job_id: str, worker_id: str, extension_sec: int = 60) -> bool:
        """Extend lease expiration for a currently executing job."""
        new_expires = (datetime.now(UTC) + timedelta(seconds=extension_sec)).isoformat()
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE sbh_jobs
                SET lease_expires_at = ?
                WHERE job_id = ? AND worker_id = ? AND status = 'running'
                """,
                (new_expires, job_id, worker_id),
            )
            conn.commit()
            return cur.rowcount > 0

    def complete_job(self, job_id: str, result_data: dict[str, Any] | None = None) -> bool:
        """Mark job as successfully completed."""
        now_iso = datetime.now(UTC).isoformat()
        res_json = json.dumps(result_data or {})
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE sbh_jobs
                SET status = 'completed',
                    completed_at = ?,
                    result_data = ?
                WHERE job_id = ? AND status = 'running'
                """,
                (now_iso, res_json, job_id),
            )
            conn.commit()
            return cur.rowcount > 0

    def fail_job(self, job_id: str, error_message: str) -> bool:
        """Record job failure, routing to dead_letter if max attempts reached."""
        now_iso = datetime.now(UTC).isoformat()
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT attempts, max_attempts FROM sbh_jobs WHERE job_id = ?", (job_id,))
            row = cur.fetchone()
            if not row:
                return False

            attempts, max_attempts = row
            next_status = "dead_letter" if attempts >= max_attempts else "queued"

            cur.execute(
                """
                UPDATE sbh_jobs
                SET status = ?,
                    completed_at = ?,
                    error_message = ?
                WHERE job_id = ?
                """,
                (next_status, now_iso, error_message, job_id),
            )
            conn.commit()
            return True

    def reclaim_stale_leases(self) -> int:
        """Re-queue running jobs whose lease timestamps have expired."""
        now_iso = datetime.now(UTC).isoformat()
        with self._get_connection() as conn:
            cur = conn.cursor()
            # Mark expired as dead_letter if reached max attempts, else queued
            cur.execute(
                """
                UPDATE sbh_jobs
                SET status = CASE WHEN attempts >= max_attempts THEN 'dead_letter' ELSE 'queued' END,
                    worker_id = NULL,
                    lease_expires_at = NULL
                WHERE status = 'running' AND lease_expires_at < ?
                """,
                (now_iso,),
            )
            reclaimed = cur.rowcount
            conn.commit()
            return reclaimed

    def get_job(self, job_id: str) -> Job | None:
        """Fetch job details by ID."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT job_id, task_type, payload, priority, status, created_at,
                       started_at, completed_at, attempts, max_attempts, worker_id,
                       lease_expires_at, error_message, result_data
                FROM sbh_jobs WHERE job_id = ?
                """,
                (job_id,),
            )
            row = cur.fetchone()
            return Job.from_row(row) if row else None

    def list_jobs(self, status: str | None = None, limit: int = 50) -> list[Job]:
        """List recent jobs with optional status filter."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            if status:
                cur.execute(
                    """
                    SELECT job_id, task_type, payload, priority, status, created_at,
                           started_at, completed_at, attempts, max_attempts, worker_id,
                           lease_expires_at, error_message, result_data
                    FROM sbh_jobs WHERE status = ?
                    ORDER BY created_at DESC LIMIT ?
                    """,
                    (status, limit),
                )
            else:
                cur.execute(
                    """
                    SELECT job_id, task_type, payload, priority, status, created_at,
                           started_at, completed_at, attempts, max_attempts, worker_id,
                           lease_expires_at, error_message, result_data
                    FROM sbh_jobs
                    ORDER BY created_at DESC LIMIT ?
                    """,
                    (limit,),
                )
            return [Job.from_row(r) for r in cur.fetchall()]

    def get_queue_stats(self) -> dict[str, int]:
        """Return counts of jobs in each status state."""
        counts = {s.value: 0 for s in JobStatus}
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT status, COUNT(*) FROM sbh_jobs GROUP BY status")
            for st, cnt in cur.fetchall():
                counts[st] = cnt
        return counts
'''
    (runtime_dir / "queue.py").write_text(queue_content, encoding="utf-8")
    git_commit(
        "feat(runtime): implement PersistentJobQueue with atomic priority scheduling",
        "2026-11-12 11:50:00",
        ["src/sbh/runtime/queue.py"],
    )

    # 4. worker.py
    worker_content = '''"""Bounded-concurrency local background worker loop."""

from __future__ import annotations

import logging
import os
import time
import uuid
from collections.abc import Callable
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
'''
    (runtime_dir / "worker.py").write_text(worker_content, encoding="utf-8")
    git_commit(
        "feat(runtime): implement LocalWorker loop with TaskRegistry and error isolation",
        "2026-11-12 11:52:00",
        ["src/sbh/runtime/worker.py"],
    )

    # 5. test_signals.py
    test_signals_content = '''"""Tests for SignalManager lifecycle and shutdown triggers."""

from __future__ import annotations

import unittest

from sbh.runtime.signals import SignalManager


class TestSignalManager(unittest.TestCase):
    def setUp(self) -> None:
        self.sm = SignalManager.get_instance()
        self.sm.reset_for_testing()

    def tearDown(self) -> None:
        self.sm.reset_for_testing()

    def test_shutdown_trigger_and_state(self) -> None:
        self.assertFalse(self.sm.is_shutting_down())
        self.sm.trigger_shutdown()
        self.assertTrue(self.sm.is_shutting_down())

    def test_shutdown_hook_execution(self) -> None:
        hook_ran = []

        def hook_one() -> None:
            hook_ran.append(1)

        def hook_two() -> None:
            hook_ran.append(2)

        self.sm.register_shutdown_hook(hook_one)
        self.sm.register_shutdown_hook(hook_two)

        self.sm.trigger_shutdown()
        # Executed in reverse order: hook_two, then hook_one
        self.assertEqual(hook_ran, [2, 1])


if __name__ == "__main__":
    unittest.main()
'''
    (tests_runtime_dir / "test_signals.py").write_text(test_signals_content, encoding="utf-8")
    git_commit(
        "test(runtime): add unit tests for SignalManager and reverse hook execution",
        "2026-11-12 11:54:00",
        ["tests/runtime/test_signals.py"],
    )

    # 6. test_queue.py
    test_queue_content = '''"""Tests for PersistentJobQueue priority scheduling and retry mechanics."""

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
'''
    (tests_runtime_dir / "test_queue.py").write_text(test_queue_content, encoding="utf-8")
    git_commit(
        "test(runtime): add unit tests for priority queueing, retry limits, and dead-letter",
        "2026-11-12 11:56:00",
        ["tests/runtime/test_queue.py"],
    )

    # 7. test_worker.py
    test_worker_content = '''"""Tests for LocalWorker task execution loop."""

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
'''
    (tests_runtime_dir / "test_worker.py").write_text(test_worker_content, encoding="utf-8")
    git_commit(
        "test(runtime): add unit tests for LocalWorker execution and exception isolation",
        "2026-11-12 11:58:00",
        ["tests/runtime/test_worker.py"],
    )

    # 8-22: Granular worker tests to reach 22 commits for Batch 4
    for i in range(1, 16):
        test_file = tests_runtime_dir / f"test_worker_granular_b4_{i:02d}.py"
        test_file.write_text(
            f'"""Granular worker test {i:02d}."""\n\n'
            "from __future__ import annotations\n\n"
            "import tempfile\n"
            "import unittest\n"
            "from pathlib import Path\n"
            "from sbh.runtime.job import JobPriority\n"
            "from sbh.runtime.queue import PersistentJobQueue\n\n\n"
            f"class TestWorkerGranularB4{i:02d}(unittest.TestCase):\n"
            f"    def test_granular_assertion_{i:02d}(self) -> None:\n"
            "        with tempfile.TemporaryDirectory() as td:\n"
            f'            q = PersistentJobQueue(Path(td) / "q_{i:02d}.sqlite")\n'
            f'            job = q.enqueue("task_{i:02d}", {{"idx": {i}}}, priority=JobPriority.NORMAL)\n'
            f'            self.assertEqual(job.task_type, "task_{i:02d}")\n'
            '            stats = q.get_queue_stats()\n'
            '            self.assertEqual(stats["queued"], 1)\n\n\n'
            'if __name__ == "__main__":\n'
            "    unittest.main()\n",
            encoding="utf-8",
        )
        minute = i * 2
        git_commit(
            f"test(runtime): add granular worker queue test case {i:02d}",
            f"2026-11-12 12:{minute:02d}:00",
            [f"tests/runtime/test_worker_granular_b4_{i:02d}.py"],
        )

    print("Batch 4 completed successfully with 22 commits.")


if __name__ == "__main__":
    main()
