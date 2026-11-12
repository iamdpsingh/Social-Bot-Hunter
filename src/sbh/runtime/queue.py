"""Persistent SQLite-backed task queue with priority scheduling and lease management."""

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
