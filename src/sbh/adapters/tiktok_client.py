"""TikTok Display and Research API client protocol and mock fixture player."""

from __future__ import annotations

from typing import Any, Protocol


class TikTokApiClient(Protocol):
    """Protocol defining TikTok API client interactions."""

    def get_user_info(self, username: str) -> dict[str, Any]:
        """Fetch user profile information from TikTok Research/Display API."""
        ...

    def query_videos(
        self, username: str, max_count: int = 20, cursor: int | None = None
    ) -> dict[str, Any]:
        """Query public videos published by username."""
        ...
