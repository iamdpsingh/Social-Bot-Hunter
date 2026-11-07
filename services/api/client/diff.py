"""Scan Diff subclient for SocialBotHunterClient SDK."""

from __future__ import annotations

from typing import Any

from services.api.client.session import ApiSession
from services.api.schemas import ScanDiffResponse


class DiffClient:
    """Client for multi-scan comparisons and diffing."""

    def __init__(self, session: ApiSession) -> None:
        self.session = session

    def compare(self, scan_a_id: str, scan_b_id: str) -> ScanDiffResponse:
        """Fetch diff comparison between two investigation scans."""
        res = self.session.get(
            "/api/v1/diff",
            params={"scan_a": scan_a_id, "scan_b": scan_b_id},
        )
        return ScanDiffResponse.model_validate(res.json())

    def get_raw_diff(self, scan_a_id: str, scan_b_id: str) -> dict[str, Any]:
        """Fetch raw JSON diff dictionary."""
        res = self.session.get(
            "/api/v1/diff",
            params={"scan_a": scan_a_id, "scan_b": scan_b_id},
        )
        return res.json()
