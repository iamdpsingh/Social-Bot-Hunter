"""Platform capabilities sub-client."""

from __future__ import annotations

from services.api.client.session import ApiSession


class CapabilitiesClient:
    """Client for platform capability endpoints."""

    def __init__(self, session: ApiSession) -> None:
        self.session = session

    def capabilities_path(self) -> str:
        return "/api/v1/capabilities"
