"""Quarantine record schemas."""

from __future__ import annotations

from pydantic import BaseModel


class QuarantineItemResponse(BaseModel):
    """Quarantine dead-letter item view."""

    id: str
    scan_id: str
    entity: str
    source_ref: str
    kind: str
    reasons: list[str]
    created_at: str
