"""Dataset import sub-client."""

from __future__ import annotations

from services.api.client.session import ApiSession


class ImportsClient:
    """Client for dataset import endpoints."""

    def __init__(self, session: ApiSession) -> None:
        self.session = session

    def import_path(self) -> str:
        return "/api/v1/imports/synthetic-demo"
