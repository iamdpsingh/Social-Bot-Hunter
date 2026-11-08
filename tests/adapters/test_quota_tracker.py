"""Tests for PlatformQuotaTracker unit consumption and limits."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from sbh.adapters.errors import QuotaExceededError
from sbh.adapters.quota import PlatformQuotaTracker


def test_quota_tracker_initial_state() -> None:
    tracker = PlatformQuotaTracker(platform="youtube", daily_limit=10000)
    assert tracker.platform == "youtube"
    assert tracker.daily_limit == 10000
    assert tracker.units_used == 0
    assert tracker.remaining_units == 10000
    assert tracker.usage_ratio == 0.0
    assert not tracker.is_warning
    assert not tracker.is_exhausted


def test_quota_tracker_consumption() -> None:
    tracker = PlatformQuotaTracker(platform="youtube", daily_limit=10000)
    rem = tracker.consume(5, operation_name="channels.list")
    assert rem == 9995
    assert tracker.units_used == 5


def test_quota_tracker_warning_threshold() -> None:
    tracker = PlatformQuotaTracker(platform="youtube", daily_limit=10000, warning_ratio=0.8)
    tracker.consume(7999)
    assert not tracker.is_warning
    tracker.consume(1)
    assert tracker.is_warning


def test_quota_tracker_exhaustion_raises() -> None:
    tracker = PlatformQuotaTracker(platform="youtube", daily_limit=100)
    tracker.consume(95)
    with pytest.raises(QuotaExceededError) as exc_info:
        tracker.consume(10, operation_name="search.list")
    assert exc_info.value.units_used == 95
    assert exc_info.value.daily_limit == 100


def test_quota_tracker_reset_new_day() -> None:
    yesterday = datetime.now(UTC) - timedelta(days=1)
    tracker = PlatformQuotaTracker(
        platform="youtube",
        daily_limit=10000,
        units_used=5000,
        reset_epoch=yesterday,
    )
    assert tracker.units_used == 5000
    reset = tracker.reset_if_new_day()
    assert reset
    assert tracker.units_used == 0
