from __future__ import annotations

import pytest

from sbh.adapters.errors import AuthenticationError, EntityNotFoundError, RateLimitExceededError
from sbh.adapters.linkedin_client import MockLinkedInClient


def test_mock_linkedin_client_organization() -> None:
    client = MockLinkedInClient()
    org = client.get_organization("tech_corp")
    assert org["name"] == "Tech Corp International"
    assert org["follower_count"] == 250000


def test_mock_linkedin_client_member() -> None:
    client = MockLinkedInClient()
    mem = client.get_member_profile("satyanadella")
    assert mem["name"] == "Satya Nadella"
    assert mem["is_influencer"] is True


def test_mock_linkedin_client_exceptions() -> None:
    client = MockLinkedInClient()
    with pytest.raises(EntityNotFoundError):
        client.get_organization("unknown_corp")

    with pytest.raises(AuthenticationError):
        client.get_organization("auth_error_org")

    with pytest.raises(RateLimitExceededError):
        client.get_organization("rate_limited_org")


def test_mock_linkedin_client_posts() -> None:
    client = MockLinkedInClient()
    res = client.query_posts("10001", count=5)
    assert len(res["elements"]) == 2
    assert "open-source" in res["elements"][0]["text"]
