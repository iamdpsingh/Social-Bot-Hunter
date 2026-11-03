"""Asynchronous background worker engine with priority queueing and retry backoff.

Orchestrates multi-threaded scan processing, graceful cancellation, watchdog heartbeats,
and automatic resumption across transient failures.
"""

from __future__ import annotations

import logging
import queue
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from sbh.pipeline.events import EventType, ScanEvent, broadcaster
from sbh.pipeline.state import ScanStage, ScanStateMachine, ScanStatus
from sbh.storage.database import Database

logger = logging.getLogger(__name__)


class TaskPriority(int, Enum):
    """Execution priority levels for scan jobs (lower value = higher priority)."""

    CRITICAL = 1
    HIGH = 2
    NORMAL = 5
    LOW = 10


class TaskStatus(str, Enum):
    """Lifecycle status of a background worker task."""

    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRY_PENDING = "retry_pending"


@dataclass
class ScanTask:
    """A unit of execution representing an asynchronous investigation job."""

    scan_id: str
    task_id: str = field(default_factory=lambda: f"task_{uuid4().hex[:12]}")
    priority: TaskPriority = TaskPriority.NORMAL
    max_retries: int = 3
    retry_count: int = 0
    enqueued_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    cancellation_requested: threading.Event = field(default_factory=threading.Event)
    params: dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.QUEUED
    error_message: str | None = None

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, ScanTask):
            return NotImplemented
        # Order by priority value (lower first), then by enqueued time
        return (self.priority.value, self.enqueued_at) < (other.priority.value, other.enqueued_at)

    def cancel(self) -> None:
        """Signal cancellation request to the executing worker."""
        self.cancellation_requested.set()
        self.status = TaskStatus.CANCELLED


class BoundedJobQueue:
    """Thread-safe priority queue preventing duplicate scans and queue overflow."""

    def __init__(self, maxsize: int = 200) -> None:
        self._maxsize = maxsize
        self._queue: queue.PriorityQueue[tuple[int, float, ScanTask]] = queue.PriorityQueue(maxsize=maxsize)
        self._lock = threading.Lock()
        self._active_scans: dict[str, ScanTask] = {}  # scan_id -> ScanTask

    def submit(self, task: ScanTask) -> bool:
        """Enqueue task if scan is not already pending or running."""
        with self._lock:
            if task.scan_id in self._active_scans:
                existing = self._active_scans[task.scan_id]
                if existing.status in {TaskStatus.QUEUED, TaskStatus.RUNNING}:
                    logger.warning("Scan '%s' is already active (%s)", task.scan_id, existing.status)
                    return False

            self._active_scans[task.scan_id] = task
            try:
                # tuple of (priority, timestamp, task) for stable ordering
                self._queue.put_nowait((task.priority.value, task.enqueued_at.timestamp(), task))
                return True
            except queue.Full:
                self._active_scans.pop(task.scan_id, None)
                logger.error("Job queue is full (maxsize=%d)", self._maxsize)
                return False

    def get(self, timeout: float = 1.0) -> ScanTask | None:
        """Retrieve next highest-priority task."""
        try:
            _, _, task = self._queue.get(timeout=timeout)
            return task
        except queue.Empty:
            return None

    def task_done(self) -> None:
        """Mark task as done in underlying priority queue."""
        self._queue.task_done()

    def get_task(self, scan_id: str) -> ScanTask | None:
        """Lookup active or recent task by scan_id."""
        with self._lock:
            return self._active_scans.get(scan_id)

    def cancel(self, scan_id: str) -> bool:
        """Cancel a pending or running scan task."""
        with self._lock:
            task = self._active_scans.get(scan_id)
            if task:
                task.cancel()
                return True
            return False

    def size(self) -> int:
        """Number of items currently queued."""
        return self._queue.qsize()

    def clear(self) -> None:
        """Clear the queue (used for testing)."""
        with self._lock:
            while not self._queue.empty():
                try:
                    self._queue.get_nowait()
                    self._queue.task_done()
                except queue.Empty:
                    break
            self._active_scans.clear()


class WorkerPool:
    """Thread pool executing background investigation scan tasks."""

    def __init__(
        self,
        db: Database,
        worker_count: int = 2,
        max_queue_size: int = 100,
        runner_fn: Callable[[str, dict[str, Any], threading.Event], Any] | None = None,
    ) -> None:
        self.db = db
        self.worker_count = worker_count
        self.queue = BoundedJobQueue(maxsize=max_queue_size)
        self.runner_fn = runner_fn
        self._workers: list[threading.Thread] = []
        self._shutdown_event = threading.Event()
        self._heartbeats: dict[str, float] = {}

    def start(self) -> None:
        """Start worker threads."""
        self._shutdown_event.clear()
        for i in range(self.worker_count):
            name = f"sbh-worker-{i+1}"
            thread = threading.Thread(target=self._worker_loop, name=name, daemon=True)
            self._workers.append(thread)
            thread.start()
        logger.info("Started %d background worker threads", self.worker_count)

    def stop(self, timeout: float = 5.0) -> None:
        """Gracefully signal workers to stop and wait for completion."""
        self._shutdown_event.set()
        for thread in self._workers:
            thread.join(timeout=timeout)
        self._workers.clear()
        logger.info("Worker pool stopped")

    def submit_scan(
        self,
        scan_id: str,
        priority: TaskPriority = TaskPriority.NORMAL,
        params: dict[str, Any] | None = None,
    ) -> bool:
        """Submit a scan ID to the worker queue."""
        task = ScanTask(scan_id=scan_id, priority=priority, params=params or {})
        enqueued = self.queue.submit(task)
        if enqueued:
            broadcaster.publish(
                ScanEvent.create(
                    scan_id=scan_id,
                    event_type=EventType.QUEUED,
                    stage=ScanStage.INITIALIZE.value,
                    progress_pct=0.0,
                    message="Scan queued for background execution",
                    details={"task_id": task.task_id, "priority": priority.name},
                )
            )
        return enqueued

    def cancel_scan(self, scan_id: str) -> bool:
        """Cancel a queued or actively running scan."""
        cancelled = self.queue.cancel(scan_id)
        if cancelled:
            broadcaster.publish(
                ScanEvent.create(
                    scan_id=scan_id,
                    event_type=EventType.CANCELLED,
                    stage="execution",
                    progress_pct=0.0,
                    message="Cancellation requested by user",
                )
            )
            # Update state machine if scan is present
            try:
                sm = ScanStateMachine(self.db, scan_id)
                if sm.can_transition(ScanStatus.CANCELLED):
                    sm.transition(ScanStatus.CANCELLED, reason="Cancelled by user")
            except Exception as e:
                logger.debug("Failed updating state machine on cancellation: %s", e)
        return cancelled

    def is_running(self) -> bool:
        """Check if any worker thread is alive."""
        return any(t.is_alive() for t in self._workers)

    def _worker_loop(self) -> None:
        """Main loop executed by each worker thread."""
        thread_name = threading.current_thread().name

        while not self._shutdown_event.is_set():
            self._heartbeats[thread_name] = time.time()
            task = self.queue.get(timeout=0.5)
            if not task:
                continue

            if task.cancellation_requested.is_set():
                task.status = TaskStatus.CANCELLED
                self.queue.task_done()
                continue

            self._process_task(task)
            self.queue.task_done()

    def _process_task(self, task: ScanTask) -> None:
        """Execute a single scan task with transition guards and error handling."""
        scan_id = task.scan_id
        sm = ScanStateMachine(self.db, scan_id)
        task.status = TaskStatus.RUNNING

        try:
            # Transition to running
            if sm.can_transition(ScanStatus.RUNNING):
                sm.transition(ScanStatus.RUNNING, actor=threading.current_thread().name)

            # Check for cancellation before expensive work
            if task.cancellation_requested.is_set():
                sm.transition(ScanStatus.CANCELLED, reason="Cancelled before execution")
                task.status = TaskStatus.CANCELLED
                return

            # Invoke custom runner function if provided
            if self.runner_fn:
                self.runner_fn(scan_id, task.params, task.cancellation_requested)
            else:
                # Default heartbeat progression if no runner attached (for testing)
                time.sleep(0.05)

            # Transition to complete if no errors and not cancelled
            if task.cancellation_requested.is_set():
                if sm.can_transition(ScanStatus.CANCELLED):
                    sm.transition(ScanStatus.CANCELLED, reason="Cancelled during execution")
                task.status = TaskStatus.CANCELLED
            elif sm.can_transition(ScanStatus.COMPLETED):
                sm.transition(ScanStatus.COMPLETED, actor=threading.current_thread().name)
                task.status = TaskStatus.SUCCEEDED

        except Exception as exc:
            logger.exception("Scan '%s' failed in worker: %s", scan_id, exc)
            task.error_message = str(exc)

            # Evaluate retry with exponential backoff
            if task.retry_count < task.max_retries and not task.cancellation_requested.is_set():
                task.retry_count += 1
                task.status = TaskStatus.RETRY_PENDING
                backoff_sec = 0.1 * (2 ** (task.retry_count - 1))
                logger.info("Retrying scan '%s' (attempt %d/%d) in %.2fs",
                            scan_id, task.retry_count, task.max_retries, backoff_sec)
                time.sleep(backoff_sec)
                self.queue.submit(task)
            else:
                task.status = TaskStatus.FAILED
                if sm.can_transition(ScanStatus.FAILED):
                    sm.transition(ScanStatus.FAILED, reason=str(exc))
