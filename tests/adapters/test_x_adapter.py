"""Tests for official X (Twitter) API v2 adapter."""

from __future__ import annotations

import time

import pytest

from sbh.adapters.errors import RateLimitExceededError
from sbh.adapters.x import XAdapter
from sbh.contracts.adapter import AccessOutcome
from sbh.contracts.capabilities import CapabilityStatus
from sbh.contracts.platforms import Platform
from sbh.schemas.records import ListKind, RelationshipType


def test_x_adapter_capabilities() -> None:
    adapter = XAdapter()
    caps = adapter.capabilities()
    assert len(caps) == 4
    for cap in caps:
        assert cap.platform == Platform.X
        assert cap.status == CapabilityStatus.VERIFIED
        assert cap.supported is True


def test_x_user_lookup_success() -> None:
    adapter = XAdapter()
    page = adapter.lookup_account("elonmusk")
    assert page.outcome == AccessOutcome.OK
    assert len(page.items) == 1
    user = page.items[0]
    assert user.platform == Platform.X.value
    assert user.username == "@elonmusk"
    assert user.follower_count == 195000000
    assert user.following_count == 750
    assert user.post_count == 48000
    assert user.is_verified is True
    assert user.has_bio is True


def test_x_user_lookup_not_found() -> None:
    adapter = XAdapter()
    page = adapter.lookup_account("nonexistent")
    assert page.outcome == AccessOutcome.UNAVAILABLE
    assert len(page.items) == 0
    assert "not found" in (page.limitation or "").lower()


def test_x_followers_pagination() -> None:
    adapter = XAdapter()
    p1 = adapter.list_relationships("44196397", ListKind.FOLLOWERS)
    assert p1.outcome == AccessOutcome.OK
    assert len(p1.items) == 2
    assert p1.items[0].relationship_type == RelationshipType.FOLLOWS
    assert p1.next_cursor == "token_page_2"

    p2 = adapter.list_relationships("44196397", ListKind.FOLLOWERS, cursor=p1.next_cursor)
    assert p2.outcome == AccessOutcome.OK
    assert len(p2.items) == 1
    assert p2.next_cursor is None


def test_x_following_listing() -> None:
    adapter = XAdapter()
    page = adapter.list_relationships("44196397", ListKind.FOLLOWING)
    assert page.outcome == AccessOutcome.OK
    assert len(page.items) == 1
    assert page.items[0].source_account_id == "44196397"
    assert page.items[0].target_account_id == "2001"


def test_x_content_listing_with_simhash() -> None:
    adapter = XAdapter()
    page = adapter.list_content("44196397")
    assert page.outcome == AccessOutcome.OK
    assert len(page.items) == 2
    tweet = page.items[0]
    assert tweet.platform == Platform.X.value
    assert tweet.platform_content_id == "1850000000000000001"
    assert tweet.simhash is not None and tweet.simhash != 0
    assert tweet.repost_count == 5200
    assert tweet.like_count == 35000
    assert page.next_cursor == "token_tweets_2"


def test_x_rate_limit_blocking() -> None:
    adapter = XAdapter()
    limiter = adapter.rate_limiters["lookup"]
    limiter.remaining = 0
    limiter.reset_epoch = time.time() + 60.0

    with pytest.raises(RateLimitExceededError):
        adapter.lookup_account("elonmusk")
