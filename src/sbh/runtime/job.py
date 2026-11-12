"""Job abstraction and lifecycle status models for background workers."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import IntEnum, StrEnum
from typing import Any


class JobStatus(StrEnum):
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
