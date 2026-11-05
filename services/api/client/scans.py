"""Scan lifecycle operations sub-client."""

from __future__ import annotations

from typing import Any

from services.api.client.session import ApiSession


class ScansClient:
    """Client for scan job endpoints."""

    def __init__(self, session: ApiSession) -> None:
        self.session = session

    def scans_path(self) -> str:
        return "/api/v1/scans"

    def get_relationships(
        self,
        scan_id: str,
        relationship_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        params = {"limit": limit, "offset": offset}
        if relationship_type:
            params["relationship_type"] = relationship_type
        return self._session.get(f"/api/v1/scans/{scan_id}/relationships", params=params)

    def export_csv(self, scan_id: str) -> str:
        res = self._session.request("GET", f"/api/v1/scans/{scan_id}/export/csv")
        return res.text

    def export_json(self, scan_id: str) -> dict[str, Any]:
        return self._session.get(f"/api/v1/scans/{scan_id}/export/json")
