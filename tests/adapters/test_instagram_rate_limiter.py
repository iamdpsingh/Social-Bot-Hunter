from __future__ import annotations

import time

import pytest

from sbh.adapters.errors import RateLimitExceededError
from sbh.adapters.rate_limiter import EndpointRateLimiter


def test_instagram_rate_limiter_hourly_window() -> None:
    limiter = EndpointRateLimiter(endpoint="instagram:business_discovery", limit=200, remaining=200)
    assert not limiter.is_limited
    assert limiter.remaining == 200

    future_reset = time.time() + 3600.0
    headers = {
        "x-rate-limit-limit": "200",
        "x-rate-limit-remaining": "0",
        "x-rate-limit-reset": str(future_reset),
    }
    limiter.update_from_headers(headers)
    assert limiter.remaining == 0
    assert limiter.is_limited

    with pytest.raises(RateLimitExceededError) as exc_info:
        limiter.check_or_raise(platform="instagram")
    assert exc_info.value.retry_after_seconds > 0
