"""Investigation reports sub-client."""

from __future__ import annotations

from services.api.client.session import ApiSession


class ReportsClient:
    """Client for report endpoints."""

    def __init__(self, session: ApiSession) -> None:
        self.session = session

    def report_path(self, scan_id: str) -> str:
        return f"/api/v1/scans/{scan_id}/report"
