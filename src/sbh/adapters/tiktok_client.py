"""TikTok Display and Research API client protocol and mock fixture player."""

from __future__ import annotations

import json
from typing import Any, Protocol, cast

from sbh.adapters.errors import (
    AuthenticationError,
    EntityNotFoundError,
    RateLimitExceededError,
)


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


class MockTikTokClient:
    """Offline mock TikTok Research & Commercial API fixture replay player."""

    def __init__(self) -> None:
        self.call_history: list[dict[str, Any]] = []
        self._users: dict[str, dict[str, Any]] = {
            "dance_creator": {
                "username": "dance_creator",
                "display_name": "Dance Trends Daily",
                "bio_description": "Choreography tutorials & dance trends ✨ Business: dance@example.com",
                "avatar_url": "https://p16-sign-va.tiktokcdn.com/tos-maliva-avt-0068/avatar1.jpg",
                "is_verified": True,
                "follower_count": 185000,
                "following_count": 312,
                "likes_count": 2400000,
                "video_count": 89,
                "is_private": False,
                "is_underage": False,
            },
            "bot_amplifier": {
                "username": "bot_amplifier",
                "display_name": "Free Coins Generator",
                "bio_description": "CLAIM FREE COINS NOW ⏩ link in bio",
                "avatar_url": "https://p16-sign-va.tiktokcdn.com/tos-maliva-avt-0068/avatar_bot.jpg",
                "is_verified": False,
                "follower_count": 5,
                "following_count": 8900,
                "likes_count": 12,
                "video_count": 14,
                "is_private": False,
                "is_underage": False,
            },
        }
        self._videos: dict[str, list[dict[str, Any]]] = {
            "dance_creator": [
                {
                    "id": "710000000001",
                    "video_description": "New summer choreography challenge! Duet this #dance #trend #viral",
                    "create_time": 1731050000,
                    "like_count": 45000,
                    "comment_count": 890,
                    "share_count": 2300,
                    "view_count": 520000,
                },
                {
                    "id": "710000000002",
                    "video_description": "Step by step breakdown of the bridge footwork #tutorial",
                    "create_time": 1730950000,
                    "like_count": 28000,
                    "comment_count": 340,
                    "share_count": 1100,
                    "view_count": 310000,
                },
            ],
            "bot_amplifier": [
                {
                    "id": "710000009999",
                    "video_description": "Click link now for 10000 free coins no human verification #freecoins",
                    "create_time": 1731060000,
                    "like_count": 1,
                    "comment_count": 0,
                    "share_count": 0,
                    "view_count": 45,
                }
            ],
        }

    def get_user_info(self, username: str) -> dict[str, Any]:
        """Fetch user profile information from TikTok Research API mock."""
        handle = username.lstrip("@").lower()
        self.call_history.append({"method": "get_user_info", "username": handle})

        if handle == "private_user":
            return {
                "username": "private_user",
                "display_name": "Private Account",
                "bio_description": "",
                "avatar_url": "",
                "is_verified": False,
                "follower_count": 0,
                "following_count": 0,
                "likes_count": 0,
                "video_count": 0,
                "is_private": True,
                "is_underage": False,
            }

        if handle == "underage_user":
            return {
                "username": "underage_user",
                "display_name": "Youth Creator",
                "bio_description": "",
                "avatar_url": "",
                "is_verified": False,
                "follower_count": 0,
                "following_count": 0,
                "likes_count": 0,
                "video_count": 0,
                "is_private": False,
                "is_underage": True,
            }

        if handle == "auth_error_user":
            raise AuthenticationError(
                "Invalid TikTok Research API client secret or bearer token",
                platform="tiktok",
            )

        if handle == "rate_limited_user":
            raise RateLimitExceededError(
                "TikTok Research API rate limit reached (120 req/min)",
                platform="tiktok",
                retry_after_seconds=60,
            )

        if handle not in self._users:
            raise EntityNotFoundError(
                f"TikTok account '@{handle}' was not found.",
                platform="tiktok",
                entity_id=handle,
            )

        return cast(dict[str, Any], json.loads(json.dumps(self._users[handle])))
