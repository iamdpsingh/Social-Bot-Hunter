"""Instagram Graph API client protocol and offline mock fixture player."""

from __future__ import annotations

import json
from typing import Any, Protocol, cast

from sbh.adapters.errors import (
    AuthenticationError,
    EntityNotFoundError,
    RateLimitExceededError,
)


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


class MockInstagramClient:
    """Offline mock Instagram Graph API client replay fixture player."""

    def __init__(self) -> None:
        self.call_history: list[dict[str, Any]] = []
        self._accounts: dict[str, dict[str, Any]] = {
            "creator_brand": {
                "id": "1784140001",
                "ig_id": "1784140001",
                "username": "creator_brand",
                "name": "Creator Brand Official",
                "biography": "Official creator and media brand. Verified account.",
                "profile_picture_url": "https://scontent.cdninstagram.com/v/t51.2885-19/avatar1.jpg",
                "followers_count": 45000,
                "follows_count": 120,
                "media_count": 310,
                "website": "https://brand.example.com",
                "account_type": "BUSINESS",
                "media": {
                    "data": [
                        {
                            "id": "18001001",
                            "caption": "Excited to launch our new automated research suite! #innovation #tech",
                            "media_type": "IMAGE",
                            "timestamp": "2026-11-08T12:00:00+0000",
                            "like_count": 1250,
                            "comments_count": 84,
                            "permalink": "https://www.instagram.com/p/DB12345/",
                        },
                        {
                            "id": "18001002",
                            "caption": "Deep dive into cross-platform bot detection methodologies. #cybersecurity",
                            "media_type": "CAROUSEL_ALBUM",
                            "timestamp": "2026-11-07T14:30:00+0000",
                            "like_count": 980,
                            "comments_count": 42,
                            "permalink": "https://www.instagram.com/p/DB12346/",
                        },
                    ]
                },
            },
            "bot_farm_node": {
                "id": "1784140099",
                "ig_id": "1784140099",
                "username": "bot_farm_node",
                "name": "Fast Promo Follow Back",
                "biography": "Follow for instant follow back! DM for promo 🚀🚀",
                "profile_picture_url": "https://scontent.cdninstagram.com/v/t51.2885-19/avatar_spam.jpg",
                "followers_count": 12,
                "follows_count": 7450,
                "media_count": 5,
                "website": "http://spam-link.ru/offer",
                "account_type": "CREATOR",
                "media": {
                    "data": [
                        {
                            "id": "18001099",
                            "caption": "Check link in bio for instant followers! #f4f #followme",
                            "media_type": "IMAGE",
                            "timestamp": "2026-11-08T09:15:00+0000",
                            "like_count": 3,
                            "comments_count": 1,
                            "permalink": "https://www.instagram.com/p/DB99999/",
                        }
                    ]
                },
            },
        }

    def business_discovery(
        self, target_username: str, fields: list[str] | None = None
    ) -> dict[str, Any]:
        """Query Instagram Business Discovery endpoint for target username."""
        username = target_username.lstrip("@").lower()
        self.call_history.append({"method": "business_discovery", "username": username})

        if username == "personal_user":
            # Graph API returns code 100 subcode 2207050 when target is not a business/creator
            return {
                "error": {
                    "message": "User is not a business account.",
                    "type": "OAuthException",
                    "code": 100,
                    "error_subcode": 2207050,
                    "fbtrace_id": "mock_trace_personal_2207050",
                }
            }

        if username == "auth_error_user":
            raise AuthenticationError(
                "Invalid OAuth access token or missing instagram_basic permission",
                platform="instagram",
            )

        if username == "rate_limited_user":
            raise RateLimitExceededError(
                "Application request limit reached for Instagram Graph API",
                platform="instagram",
                retry_after_seconds=3600,
            )

        if username not in self._accounts:
            raise EntityNotFoundError(
                f"Instagram account '{username}' was not found.",
                platform="instagram",
                entity_id=username,
            )

        account_data = self._accounts[username]
        return {"business_discovery": cast(dict[str, Any], json.loads(json.dumps(account_data)))}

    def get_media(self, ig_user_id: str, limit: int = 25) -> dict[str, Any]:
        """Fetch media data for a user."""
        self.call_history.append({"method": "get_media", "ig_user_id": ig_user_id, "limit": limit})
        for acc in self._accounts.values():
            if acc["id"] == ig_user_id or acc["ig_id"] == ig_user_id:
                media_list = acc.get("media", {}).get("data", [])[:limit]
                return {"data": cast(list[dict[str, Any]], json.loads(json.dumps(media_list)))}
        return {"data": []}
