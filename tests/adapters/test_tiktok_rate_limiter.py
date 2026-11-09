from __future__ import annotations

from sbh.adapters.rate_limiter import EndpointRateLimiter


def test_tiktok_rate_limiter_minute_window() -> None:
    limiter = EndpointRateLimiter(endpoint="tiktok:research:user_info", limit=3, window_seconds=60.0)

    assert limiter.remaining == 3
    for _ in range(3):
        assert limiter.acquire() is True

    assert limiter.remaining == 0
    assert limiter.is_limited is True
    assert limiter.acquire() is False
