"""Account query sub-client."""

from __future__ import annotations

from typing import Any
from services.api.client.session import ApiSession


class AccountsClient:
    """Client for account endpoints."""

    def __init__(self, session: ApiSession) -> None:
        self.session = session

    def accounts_path(self, scan_id: str) -> str:
        return f"/api/v1/scans/{scan_id}/accounts"

    def list_accounts(
        self,
        scan_id: str,
        band: str | None = None,
        status: str | None = None,
        search: str | None = None,
        sort_by: str = "score_desc",
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"limit": limit, "offset": offset, "sort_by": sort_by}
        if band:
            params["band"] = band
        if status:
            params["status"] = status
        if search:
            params["search"] = search
        return self.session.get(self.accounts_path(scan_id), params=params)

    def get_account(self, scan_id: str, account_id: str) -> dict[str, Any]:
        return self.session.get(f"{self.accounts_path(scan_id)}/{account_id}")

    def get_evidence(self, scan_id: str, account_id: str) -> dict[str, Any]:
        return self.session.get(f"{self.accounts_path(scan_id)}/{account_id}/evidence")

    def get_features(self, scan_id: str, account_id: str) -> dict[str, Any]:
        return self.session.get(f"{self.accounts_path(scan_id)}/{account_id}/features")

    def get_neighborhood(self, scan_id: str, account_id: str) -> dict[str, Any]:
        return self.session.get(f"{self.accounts_path(scan_id)}/{account_id}/neighborhood")

