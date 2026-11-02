"""Investigation report schemas."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel


class InvestigationReportResponse(BaseModel):
    """Synthesized investigation report view."""
    scan_id: str
    platform: str
    summary: dict[str, Any]
    high_risk_accounts: list[dict[str, Any]]
    candidate_clusters: list[dict[str, Any]]
    limitations: list[str]
