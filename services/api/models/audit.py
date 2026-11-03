"""Audit event schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class AuditEventResponse(BaseModel):
    """Audit log entry view."""

    id: str
    occurred_at: str
    actor: str
    action: str
    subject_type: str
    subject_id: str | None = None
    details: dict[str, Any] = {}
