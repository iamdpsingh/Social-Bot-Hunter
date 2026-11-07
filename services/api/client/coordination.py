"""Coordination subclient for SocialBotHunterClient SDK."""

from __future__ import annotations

from typing import Any

from services.api.client.session import ApiSession
from services.api.schemas import CoordinationSummaryResponse


class CoordinationClient:
    """Client for retrieving coordinated activity and SimHash clusters."""

    def __init__(self, session: ApiSession) -> None:
        self.session = session

    def get_coordination(
        self,
        scan_id: str,
        burst_window_seconds: float = 60.0,
        min_similarity_distance: int = 4,
    ) -> CoordinationSummaryResponse:
        """Fetch coordinated activity summary for an investigation scan."""
        res = self.session.get(
            f"/api/v1/scans/{scan_id}/coordination",
            params={
                "burst_window_seconds": burst_window_seconds,
                "min_similarity_distance": min_similarity_distance,
            },
        )
        return CoordinationSummaryResponse.model_validate(res.json())

    def get_raw_coordination(self, scan_id: str) -> dict[str, Any]:
        """Fetch raw JSON dictionary for coordination analysis."""
        res = self.session.get(f"/api/v1/scans/{scan_id}/coordination")
        return res.json()
