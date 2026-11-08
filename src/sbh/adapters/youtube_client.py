"""HTTP client abstraction and offline mock client for YouTube Data API v3."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol


class YouTubeApiClient(Protocol):
    """Protocol for interacting with YouTube Data API v3 endpoints."""

    def get_channel(self, identifier: str, is_handle: bool = False) -> dict[str, Any]:
        """Fetch channel resource via channels.list."""
        ...

    def list_playlist_items(
        self, playlist_id: str, max_results: int = 50, page_token: str | None = None
    ) -> dict[str, Any]:
        """Fetch upload playlist items via playlistItems.list."""
        ...

    def list_subscriptions(
        self, channel_id: str, max_results: int = 50, page_token: str | None = None
    ) -> dict[str, Any]:
        """Fetch public channel subscriptions via subscriptions.list."""
        ...


class MockYouTubeClient:
    """Offline mock client reading recorded replay fixtures."""

    def __init__(self, fixtures_dir: Path | None = None) -> None:
        self.fixtures_dir = fixtures_dir or (
            Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "youtube"
        )
        self.call_history: list[dict[str, Any]] = []

    def _read_fixture(self, filename: str) -> dict[str, Any]:
        path = self.fixtures_dir / filename
        if not path.exists():
            return {"items": []}
        return json.loads(path.read_text(encoding="utf-8"))

    def get_channel(self, identifier: str, is_handle: bool = False) -> dict[str, Any]:
        self.call_history.append({"endpoint": "channels", "identifier": identifier, "is_handle": is_handle})
        if identifier in ("nonexistent", "@nonexistent", "UCnonexistentchannelid12"):
            return self._read_fixture("channel_lookup_empty.json")
        return self._read_fixture("channel_lookup_success.json")

    def list_playlist_items(
        self, playlist_id: str, max_results: int = 50, page_token: str | None = None
    ) -> dict[str, Any]:
        self.call_history.append({"endpoint": "playlistItems", "playlist_id": playlist_id, "token": page_token})
        return self._read_fixture("playlist_items_success.json")

    def list_subscriptions(
        self, channel_id: str, max_results: int = 50, page_token: str | None = None
    ) -> dict[str, Any]:
        self.call_history.append({"endpoint": "subscriptions", "channel_id": channel_id, "token": page_token})
        return self._read_fixture("subscriptions_success.json")
