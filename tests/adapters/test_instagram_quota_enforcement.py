from __future__ import annotations

import pytest

from sbh.adapters.errors import QuotaExceededError
from sbh.adapters.instagram import InstagramAdapter
from sbh.adapters.quota import PlatformQuotaTracker


def test_instagram_quota_consumption_and_tracking() -> None:
    tracker = PlatformQuotaTracker(platform="instagram", daily_limit=10)
    adapter = InstagramAdapter(quota_tracker=tracker)

    assert tracker.remaining_units == 10
    adapter.lookup_account("creator_brand")
    assert tracker.remaining_units == 9

    adapter.list_content("creator_brand", limit=5)
    assert tracker.remaining_units == 8


def test_instagram_quota_exhaustion_exception() -> None:
    tracker = PlatformQuotaTracker(platform="instagram", daily_limit=1)
    adapter = InstagramAdapter(quota_tracker=tracker)

    adapter.lookup_account("creator_brand")
    with pytest.raises(QuotaExceededError, match="Quota exceeded for instagram"):
        adapter.lookup_account("creator_brand")
