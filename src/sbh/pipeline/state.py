"""Scan state machine transitions, stage definitions, and atomic checkpoints.

Provides formal state validation, optimistic locking transitions, and persistent stage
progress tracking for resumable background pipeline jobs.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from sbh.pipeline.events import EventType, ScanEvent, broadcaster
from sbh.shared import jsonutil
from sbh.shared.errors import InvalidTransitionError
from sbh.storage.audit import AuditRepository
from sbh.storage.database import Database
from sbh.storage.scans import ScanRepository


class ScanStatus(str, Enum):
    """Lifecycle statuses of an investigation scan."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "complete"
    PARTIAL = "partial"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScanStage(str, Enum):
    """Discrete, ordered execution stages in the ingestion and analytics pipeline."""

    INITIALIZE = "initialize"
    VALIDATE = "validate"
    INGEST_ACCOUNTS = "ingest_accounts"
    INGEST_RELATIONSHIPS = "ingest_relationships"
    INGEST_CONTENT = "ingest_content"
    EXTRACT_FEATURES = "extract_features"
    SCORE_RISK = "score_risk"
    DETECT_CLUSTERS = "detect_clusters"
    FINALIZE = "finalize"

    @property
    def weight(self) -> float:
        """Relative progress weight (percentage points out of 100)."""
        weights: dict[ScanStage, float] = {
            ScanStage.INITIALIZE: 5.0,
            ScanStage.VALIDATE: 10.0,
            ScanStage.INGEST_ACCOUNTS: 15.0,
            ScanStage.INGEST_RELATIONSHIPS: 20.0,
            ScanStage.INGEST_CONTENT: 10.0,
            ScanStage.EXTRACT_FEATURES: 15.0,
            ScanStage.SCORE_RISK: 15.0,
            ScanStage.DETECT_CLUSTERS: 8.0,
            ScanStage.FINALIZE: 2.0,
        }
        return weights.get(self, 10.0)


# Allowed state transitions: source -> set of targets
LEGAL_TRANSITIONS: dict[ScanStatus, set[ScanStatus]] = {
    ScanStatus.PENDING: {ScanStatus.RUNNING, ScanStatus.CANCELLED, ScanStatus.FAILED},
    ScanStatus.RUNNING: {
        ScanStatus.COMPLETED,
        ScanStatus.PARTIAL,
        ScanStatus.FAILED,
        ScanStatus.CANCELLED,
    },
    ScanStatus.COMPLETED: set(),
    ScanStatus.PARTIAL: set(),
    ScanStatus.FAILED: {ScanStatus.PENDING},  # allowed via retry
    ScanStatus.CANCELLED: {ScanStatus.PENDING},  # allowed via retry
}


@dataclass(frozen=True)
class CheckpointRecord:
    """Persistent stage completion marker."""

    scan_id: str
    stage: ScanStage
    processed_count: int
    total_count: int | None = None
    cursor: str | None = None
    committed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)


class ScanStateMachine:
    """Manages transactional state changes and progress notifications."""

    def __init__(self, db: Database, scan_id: str) -> None:
        self.db = db
        self.scan_id = scan_id
        self.scan_repo = ScanRepository(db)
        self.audit_repo = AuditRepository(db)

    def current_status(self) -> ScanStatus:
        """Fetch current scan status from persistent storage."""
        scan = self.scan_repo.get_scan(self.scan_id)
        if not scan:
            raise ValueError(f"Scan '{self.scan_id}' does not exist.")
        return ScanStatus(scan["status"])

    def can_transition(self, target: ScanStatus) -> bool:
        """Check whether transition to target status is valid from current status."""
        cur = self.current_status()
        return target in LEGAL_TRANSITIONS.get(cur, set())

    def transition(
        self,
        to_status: ScanStatus,
        allowed_from: Sequence[ScanStatus] | None = None,
        *,
        actor: str = "pipeline.worker",
        reason: str | None = None,
        completeness: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Conditionally transition the scan status with concurrency protection and event broadcast."""
        cur = self.current_status()
        expected = set(allowed_from) if allowed_from else LEGAL_TRANSITIONS.get(cur, set())

        if to_status not in expected:
            raise InvalidTransitionError(
                f"Cannot transition scan '{self.scan_id}' from '{cur.value}' to '{to_status.value}'"
            )

        # Atomic database transition conditional on matching source status
        valid_sources = [s.value for s in (allowed_from or [cur])]
        self.scan_repo.transition(
            self.scan_id,
            to=to_status.value,
            allowed_from=valid_sources,
            failure_reason=reason,
            completeness=completeness,
        )

        # Record audit log
        self.audit_repo.record(
            actor=actor,
            action=f"scan.transition.{to_status.value}",
            subject_type="scan",
            subject_id=self.scan_id,
            details={
                "from_status": cur.value,
                "to_status": to_status.value,
                "reason": reason,
                "extra": details or {},
            },
        )

        # Broadcast event
        ev_type = (
            EventType.COMPLETED
            if to_status == ScanStatus.COMPLETED
            else EventType.CANCELLED
            if to_status == ScanStatus.CANCELLED
            else EventType.ERROR
            if to_status == ScanStatus.FAILED
            else EventType.STARTED
            if to_status == ScanStatus.RUNNING
            else EventType.PROGRESS
        )
        broadcaster.publish(
            ScanEvent.create(
                scan_id=self.scan_id,
                event_type=ev_type,
                stage="state_transition",
                progress_pct=100.0 if to_status in {ScanStatus.COMPLETED, ScanStatus.PARTIAL} else 0.0,
                message=f"Scan transitioned to {to_status.value}" + (f": {reason}" if reason else ""),
                details=details,
            )
        )

    def record_checkpoint(self, checkpoint: CheckpointRecord) -> None:
        """Save a restart checkpoint in scan_checkpoints table and broadcast progress."""
        now = datetime.now(UTC).isoformat()
        self.db.execute(
            "INSERT INTO scan_checkpoints (scan_id, stage, processed_count, committed_at, details) "
            "VALUES (:scan_id, :stage, :count, :now, :details)",
            {
                "scan_id": checkpoint.scan_id,
                "stage": checkpoint.stage.value,
                "count": checkpoint.processed_count,
                "now": now,
                "details": jsonutil.dumps(checkpoint.metadata),
            },
        )

        # Calculate estimated overall progress
        stages = list(ScanStage)
        current_idx = stages.index(checkpoint.stage)
        cum_weight = sum(s.weight for s in stages[:current_idx])
        stage_weight = checkpoint.stage.weight
        stage_fraction = (
            min(1.0, checkpoint.processed_count / checkpoint.total_count)
            if checkpoint.total_count and checkpoint.total_count > 0
            else 0.5
        )
        total_pct = round(cum_weight + (stage_weight * stage_fraction), 1)

        broadcaster.publish(
            ScanEvent.create(
                scan_id=self.scan_id,
                event_type=EventType.CHECKPOINT,
                stage=checkpoint.stage.value,
                progress_pct=total_pct,
                message=f"Completed {checkpoint.stage.value} ({checkpoint.processed_count} records)",
                details=checkpoint.metadata,
            )
        )

    def get_latest_checkpoint(self) -> dict[str, Any] | None:
        """Fetch the most recently committed checkpoint for this scan."""
        return self.db.query_one(
            "SELECT stage, processed_count, committed_at, details "
            "FROM scan_checkpoints WHERE scan_id = :s ORDER BY committed_at DESC LIMIT 1",
            {"s": self.scan_id},
        )
