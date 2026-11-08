"""HTTP client abstraction and offline mock player for X API v2."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol, cast


class XApiClient(Protocol):
    """Protocol for interacting with X API v2 endpoints."""

    def get_user_by_username(self, username: str) -> dict[str, Any]:
        """Fetch user by handle via GET /2/users/by/username/:username."""
        ...

    def get_user_by_id(self, user_id: str) -> dict[str, Any]:
        """Fetch user by id via GET /2/users/:id."""
        ...

    def list_followers(
        self, user_id: str, pagination_token: str | None = None, max_results: int = 100
    ) -> dict[str, Any]:
        """Fetch followers via GET /2/users/:id/followers."""
        ...

    def list_following(
        self, user_id: str, pagination_token: str | None = None, max_results: int = 100
    ) -> dict[str, Any]:
        """Fetch following via GET /2/users/:id/following."""
        ...

    def list_tweets(
        self, user_id: str, pagination_token: str | None = None, max_results: int = 100
    ) -> dict[str, Any]:
        """Fetch tweets via GET /2/users/:id/tweets."""
        ...


class MockXClient:
    """Offline mock client reading recorded X API v2 replay fixtures."""

    def __init__(self, fixtures_dir: Path | None = None) -> None:
        self.fixtures_dir = fixtures_dir or (
            Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "x"
        )
        self.call_history: list[dict[str, Any]] = []

    def _read_fixture(self, filename: str) -> dict[str, Any]:
        path = self.fixtures_dir / filename
        if not path.exists():
            return {}
        return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))

    def get_user_by_username(self, username: str) -> dict[str, Any]:
        self.call_history.append({"endpoint": "users/by/username", "username": username})
        if username in ("nonexistent", "unknown_user_404"):
            return self._read_fixture("user_lookup_empty.json")
        return self._read_fixture("user_lookup_success.json")

    def get_user_by_id(self, user_id: str) -> dict[str, Any]:
        self.call_history.append({"endpoint": "users/id", "user_id": user_id})
        if user_id in ("0", "404", "nonexistent"):
            return self._read_fixture("user_lookup_empty.json")
        return self._read_fixture("user_lookup_success.json")

    def list_followers(
        self, user_id: str, pagination_token: str | None = None, max_results: int = 100
    ) -> dict[str, Any]:
        self.call_history.append({"endpoint": "users/followers", "user_id": user_id, "token": pagination_token})
        if pagination_token == "token_page_2":
            return self._read_fixture("followers_page2.json")
        return self._read_fixture("followers_page1.json")

    def list_following(
        self, user_id: str, pagination_token: str | None = None, max_results: int = 100
    ) -> dict[str, Any]:
        self.call_history.append({"endpoint": "users/following", "user_id": user_id, "token": pagination_token})
        return self._read_fixture("following_success.json")

    def list_tweets(
        self, user_id: str, pagination_token: str | None = None, max_results: int = 100
    ) -> dict[str, Any]:
        self.call_history.append({"endpoint": "users/tweets", "user_id": user_id, "token": pagination_token})
        return self._read_fixture("tweets_success.json")
