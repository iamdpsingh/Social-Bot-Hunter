from __future__ import annotations

import pytest

from sbh.adapters.errors import QuotaExceededError
from sbh.adapters.quota import PlatformQuotaTracker
from sbh.adapters.tiktok import TikTokAdapter


def test_tiktok_quota_consumption_and_tracking() -> None:
    tracker = PlatformQuotaTracker(platform="tiktok", daily_limit=10)
    adapter = TikTokAdapter(quota_tracker=tracker)

    assert tracker.remaining_units == 10
    adapter.lookup_account("@dance_creator")
    assert tracker.remaining_units == 9

    adapter.list_content("@dance_creator", limit=5)
    assert tracker.remaining_units == 8


def test_tiktok_quota_exhaustion_exception() -> None:
    tracker = PlatformQuotaTracker(platform="tiktok", daily_limit=1)
    adapter = TikTokAdapter(quota_tracker=tracker)

    adapter.lookup_account("@dance_creator")
    with pytest.raises(QuotaExceededError, match="Quota exceeded for tiktok"):
        adapter.lookup_account("@dance_creator")
