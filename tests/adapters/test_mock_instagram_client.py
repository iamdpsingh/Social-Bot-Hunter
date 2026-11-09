from __future__ import annotations

import pytest

from sbh.adapters.errors import AuthenticationError, EntityNotFoundError, RateLimitExceededError
from sbh.adapters.instagram_client import MockInstagramClient


def test_mock_instagram_client_business_discovery() -> None:
    client = MockInstagramClient()
    res = client.business_discovery("creator_brand")
    assert "business_discovery" in res
    bd = res["business_discovery"]
    assert bd["username"] == "creator_brand"
    assert bd["followers_count"] == 45000
    assert len(bd["media"]["data"]) == 2


def test_mock_instagram_client_personal_user_error() -> None:
    client = MockInstagramClient()
    res = client.business_discovery("personal_user")
    assert "error" in res
    assert res["error"]["error_subcode"] == 2207050


def test_mock_instagram_client_exceptions() -> None:
    client = MockInstagramClient()
    with pytest.raises(EntityNotFoundError):
        client.business_discovery("nonexistent_account")

    with pytest.raises(AuthenticationError):
        client.business_discovery("auth_error_user")

    with pytest.raises(RateLimitExceededError):
        client.business_discovery("rate_limited_user")
