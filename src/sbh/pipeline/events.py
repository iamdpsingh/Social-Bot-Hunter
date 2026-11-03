"""Real-time scan event streaming and pub/sub broadcaster.

Supports Server-Sent Events (SSE) formatting, event replay via Last-Event-ID,
and thread-safe in-memory fan-out across multiple active investigation observers.
"""

from __future__ import annotations

import contextlib
import json
import threading
import time
from collections import deque
from collections.abc import Iterator
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4


class EventType(str, Enum):
    """Lifecycle stages and notifications during scan execution."""

    QUEUED = "queued"
    STARTED = "started"
    STAGE_STARTED = "stage_started"
    PROGRESS = "progress"
    CHECKPOINT = "checkpoint"
    STAGE_COMPLETED = "stage_completed"
    WARNING = "warning"
    ERROR = "error"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    HEARTBEAT = "heartbeat"


@dataclass(frozen=True)
class ScanEvent:
    """A discrete, immutable progress or status event emitted by the pipeline."""

    scan_id: str
    event_id: str
    event_type: EventType
    stage: str
    progress_pct: float
    message: str
    timestamp: float = field(default_factory=time.time)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert event to serializable dictionary."""
        d = asdict(self)
        d["event_type"] = self.event_type.value
        return d

    def to_sse(self) -> str:
        """Format as a Server-Sent Event (SSE) frame."""
        payload = json.dumps(self.to_dict())
        return f"id: {self.event_id}\nevent: {self.event_type.value}\ndata: {payload}\n\n"

    @classmethod
    def create(
        cls,
        scan_id: str,
        event_type: EventType,
        stage: str,
        progress_pct: float,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> ScanEvent:
        """Helper factory creating an event with a unique ID and current timestamp."""
        return cls(
            scan_id=scan_id,
            event_id=f"evt_{uuid4().hex[:12]}",
            event_type=event_type,
            stage=stage,
            progress_pct=max(0.0, min(100.0, float(progress_pct))),
            message=message,
            timestamp=time.time(),
            details=details or {},
        )


class ScanEventBroadcaster:
    """Thread-safe event pub/sub broker with bounded per-scan history buffer."""

    def __init__(self, history_limit_per_scan: int = 500) -> None:
        self._history_limit = history_limit_per_scan
        self._lock = threading.RLock()
        # scan_id -> deque of ScanEvent
        self._history: dict[str, deque[ScanEvent]] = {}
        # scan_id -> set of subscriber queues
        self._subscribers: dict[str, list[deque[ScanEvent]]] = {}

    def publish(self, event: ScanEvent) -> None:
        """Publish an event to all active subscribers and append to replay buffer."""
        with self._lock:
            if event.scan_id not in self._history:
                self._history[event.scan_id] = deque(maxlen=self._history_limit)
            self._history[event.scan_id].append(event)

            subscribers = self._subscribers.get(event.scan_id, [])
            for sub_queue in list(subscribers):
                with contextlib.suppress(Exception):
                    sub_queue.append(event)

    def subscribe(self, scan_id: str, last_event_id: str | None = None) -> Iterator[ScanEvent]:
        """Subscribe to events for a scan, yielding historical events first if requested."""
        client_queue: deque[ScanEvent] = deque(maxlen=1000)

        with self._lock:
            # Replay historical events if last_event_id provided
            if last_event_id and scan_id in self._history:
                found = False
                for ev in self._history[scan_id]:
                    if found:
                        client_queue.append(ev)
                    elif ev.event_id == last_event_id:
                        found = True
                # If last_event_id wasn't found in buffer, replay entire buffer
                if not found:
                    for ev in self._history[scan_id]:
                        client_queue.append(ev)

            if scan_id not in self._subscribers:
                self._subscribers[scan_id] = []
            self._subscribers[scan_id].append(client_queue)

        try:
            while True:
                if client_queue:
                    yield client_queue.popleft()
                else:
                    time.sleep(0.05)
        finally:
            self.unsubscribe(scan_id, client_queue)

    def unsubscribe(self, scan_id: str, client_queue: deque[ScanEvent]) -> None:
        """Remove a subscriber queue from the scan's active listener list."""
        with self._lock:
            if scan_id in self._subscribers:
                if client_queue in self._subscribers[scan_id]:
                    self._subscribers[scan_id].remove(client_queue)
                if not self._subscribers[scan_id]:
                    del self._subscribers[scan_id]

    def get_history(self, scan_id: str, limit: int = 100) -> list[ScanEvent]:
        """Return the recent event history for a scan."""
        with self._lock:
            events = list(self._history.get(scan_id, []))
            return events[-limit:] if limit > 0 else events

    def clear(self, scan_id: str | None = None) -> None:
        """Clear event history for a scan or all scans."""
        with self._lock:
            if scan_id:
                self._history.pop(scan_id, None)
                self._subscribers.pop(scan_id, None)
            else:
                self._history.clear()
                self._subscribers.clear()


# Global singleton instance for use across API routes and worker threads
broadcaster = ScanEventBroadcaster()
