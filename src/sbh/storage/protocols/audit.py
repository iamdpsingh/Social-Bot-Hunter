"""Audit log storage protocol."""

from __future__ import annotations

from typing import Any, Mapping, Protocol, runtime_checkable


@runtime_checkable
class AuditStoreProtocol(Protocol):
    """Protocol defining compliance audit trail persistence."""

    def log_event(self, action: str, actor_id: str | None, subject_type: str | None, subject_id: str | None, details: Mapping[str, Any] | None = None) -> Mapping[str, Any]:
        """Log an immutable audit event."""
        ...

    def list_events(self, *, limit: int = 100, offset: int = 0) -> list[Mapping[str, Any]]:
        """List audit events with pagination."""
        ...

    def get_event(self, event_id: str) -> Mapping[str, Any] | None:
        """Get single audit event by ID."""
        ...
