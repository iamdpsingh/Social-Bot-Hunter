"""Relationship edge schemas."""

from __future__ import annotations

from pydantic import BaseModel


class RelationshipEdgeResponse(BaseModel):
    """Directed relationship edge view."""
    id: str
    scan_id: str
    platform: str
    source_account_id: str
    target_account_id: str
    relationship_type: str = "follows"
    observed_at: str
    verification_status: str
