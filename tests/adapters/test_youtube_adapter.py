"""Tests for official YouTube Data API v3 adapter."""

from __future__ import annotations

import pytest

from sbh.adapters.errors import QuotaExceededError
from sbh.adapters.quota import PlatformQuotaTracker
from sbh.adapters.youtube import YouTubeAdapter
from sbh.contracts.adapter import AccessOutcome
from sbh.contracts.capabilities import CapabilityStatus, Operation
from sbh.contracts.platforms import Platform
from sbh.schemas.records import ListKind


def test_youtube_adapter_capabilities() -> None:
    adapter = YouTubeAdapter()
    caps = adapter.capabilities()
    assert len(caps) == 4
    lookup_cap = next(c for c in caps if c.operation == Operation.LOOKUP_ACCOUNT)
    assert lookup_cap.status == CapabilityStatus.VERIFIED
    assert lookup_cap.supported is True

    followers_cap = next(c for c in caps if c.operation == Operation.LIST_FOLLOWERS)
    assert followers_cap.status == CapabilityStatus.REQUIRES_APPROVAL
    assert followers_cap.requires_approval is True


def test_youtube_channel_lookup_success() -> None:
    adapter = YouTubeAdapter()
    page = adapter.lookup_account("UCYO_jab_esuFRV4b17AJtAw")
    assert page.outcome == AccessOutcome.OK
    assert len(page.items) == 1
    record = page.items[0]
    assert record.platform == Platform.YOUTUBE
    assert record.display_name == "3Blue1Brown"
    assert record.handle == "@3blue1brown"
    assert record.followers_count == 6200000
    assert record.posts_count == 172
    assert record.metadata["upload_playlist_id"] == "UUYO_jab_esuFRV4b17AJtAw"


def test_youtube_channel_lookup_not_found() -> None:
    adapter = YouTubeAdapter()
    page = adapter.lookup_account("nonexistent")
    assert page.outcome == AccessOutcome.UNAVAILABLE
    assert len(page.items) == 0
    assert "not found" in (page.limitation or "").lower()


def test_youtube_subscribers_requires_approval() -> None:
    adapter = YouTubeAdapter()
    page = adapter.list_relationships("UCYO_jab_esuFRV4b17AJtAw", ListKind.FOLLOWERS)
    assert page.outcome == AccessOutcome.REQUIRES_APPROVAL
    assert "OAuth 2.0" in (page.limitation or "")
    assert len(page.items) == 0


def test_youtube_following_subscriptions() -> None:
    adapter = YouTubeAdapter()
    page = adapter.list_relationships("UCYO_jab_esuFRV4b17AJtAw", ListKind.FOLLOWING)
    assert page.outcome == AccessOutcome.OK
    assert len(page.items) == 1
    rel = page.items[0]
    assert rel.platform == Platform.YOUTUBE
    assert rel.source_account_id == "UCYO_jab_esuFRV4b17AJtAw"
    assert rel.target_account_id == "UCHnyfMqiRRG1u-2MsSQLbXA"
    assert rel.kind == ListKind.FOLLOWING


def test_youtube_list_content() -> None:
    adapter = YouTubeAdapter()
    page = adapter.list_content("UCYO_jab_esuFRV4b17AJtAw")
    assert page.outcome == AccessOutcome.OK
    assert len(page.items) == 2
    video = page.items[0]
    assert video.platform == Platform.YOUTUBE
    assert video.content_id == "spUNpyF58BY"
    assert "Fourier" in video.body
    assert video.url == "https://www.youtube.com/watch?v=spUNpyF58BY"
    assert page.next_cursor == "CAUQAA"


def test_youtube_quota_consumption() -> None:
    tracker = PlatformQuotaTracker(platform="youtube", daily_limit=10)
    adapter = YouTubeAdapter(quota_tracker=tracker)
    assert tracker.units_used == 0

    adapter.lookup_account("UCYO_jab_esuFRV4b17AJtAw")
    assert tracker.units_used == 1

    adapter.list_content("UCYO_jab_esuFRV4b17AJtAw")
    assert tracker.units_used == 2

    adapter.list_relationships("UCYO_jab_esuFRV4b17AJtAw", ListKind.FOLLOWING)
    assert tracker.units_used == 3


def test_youtube_quota_exhaustion_blocks_call() -> None:
    tracker = PlatformQuotaTracker(platform="youtube", daily_limit=2)
    adapter = YouTubeAdapter(quota_tracker=tracker)
    adapter.lookup_account("UCYO_jab_esuFRV4b17AJtAw")
    adapter.list_content("UCYO_jab_esuFRV4b17AJtAw")
    assert tracker.units_used == 2

    with pytest.raises(QuotaExceededError):
        adapter.list_relationships("UCYO_jab_esuFRV4b17AJtAw", ListKind.FOLLOWING)
