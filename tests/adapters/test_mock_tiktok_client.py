from __future__ import annotations

import pytest

from sbh.adapters.errors import AuthenticationError, EntityNotFoundError, RateLimitExceededError
from sbh.adapters.tiktok_client import MockTikTokClient


def test_mock_tiktok_client_user_info() -> None:
    client = MockTikTokClient()
    user = client.get_user_info("dance_creator")
    assert user["username"] == "dance_creator"
    assert user["follower_count"] == 185000
    assert user["is_verified"] is True
    assert user["is_private"] is False


def test_mock_tiktok_client_private_and_underage() -> None:
    client = MockTikTokClient()
    priv = client.get_user_info("private_user")
    assert priv["is_private"] is True

    youth = client.get_user_info("underage_user")
    assert youth["is_underage"] is True


def test_mock_tiktok_client_exceptions() -> None:
    client = MockTikTokClient()
    with pytest.raises(EntityNotFoundError):
        client.get_user_info("unknown_profile")

    with pytest.raises(AuthenticationError):
        client.get_user_info("auth_error_user")

    with pytest.raises(RateLimitExceededError):
        client.get_user_info("rate_limited_user")


def test_mock_tiktok_client_video_queries() -> None:
    client = MockTikTokClient()
    res = client.query_videos("dance_creator", max_count=5)
    assert len(res["videos"]) == 2
    assert res["videos"][0]["id"] == "710000000001"
