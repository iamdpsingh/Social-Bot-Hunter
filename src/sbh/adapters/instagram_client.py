"""Instagram Graph API client protocol and offline mock fixture player."""

from __future__ import annotations

from typing import Any, Protocol


class InstagramApiClient(Protocol):
    """Protocol defining required Instagram Graph API client interactions."""

    def business_discovery(
        self, target_username: str, fields: list[str] | None = None
    ) -> dict[str, Any]:
        """Query Instagram Business Discovery endpoint for a target account."""
        ...

    def get_media(self, ig_user_id: str, limit: int = 25) -> dict[str, Any]:
        """Fetch recent media for an Instagram user."""
        ...
