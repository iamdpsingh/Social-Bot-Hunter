"""Scan lifecycle operations sub-client."""

from __future__ import annotations

from services.api.client.session import ApiSession


class ScansClient:
    """Client for scan job endpoints."""

    def __init__(self, session: ApiSession) -> None:
        self.session = session

    def scans_path(self) -> str:
        return "/api/v1/scans"
