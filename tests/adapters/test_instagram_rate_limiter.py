from __future__ import annotations

from sbh.adapters.rate_limiter import EndpointRateLimiter


def test_instagram_rate_limiter_hourly_window() -> None:
    limiter = EndpointRateLimiter(endpoint="instagram:business_discovery", limit=5, window_seconds=3600.0)

    assert limiter.remaining == 5
    for _ in range(5):
        assert limiter.acquire() is True

    assert limiter.remaining == 0
    assert limiter.is_limited is True
    assert limiter.acquire() is False
