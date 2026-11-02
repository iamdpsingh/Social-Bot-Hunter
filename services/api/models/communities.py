"""Community cluster schemas."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel


class CommunityClusterResponse(BaseModel):
    """Detected coordinated cluster view."""
    id: str
    scan_id: str
    method: str
    member_count: int
    signal_strength: str
    confidence: str
    metrics: dict[str, Any] = {}
