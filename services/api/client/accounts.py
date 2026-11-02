"""Account query sub-client."""

from __future__ import annotations

from services.api.client.session import ApiSession


class AccountsClient:
    """Client for account endpoints."""

    def __init__(self, session: ApiSession) -> None:
        self.session = session

    def accounts_path(self, scan_id: str) -> str:
        return f"/api/v1/scans/{scan_id}/accounts"
