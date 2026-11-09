from __future__ import annotations

import time

import pytest

from sbh.adapters.errors import RateLimitExceededError
from sbh.adapters.rate_limiter import EndpointRateLimiter


def test_tiktok_rate_limiter_minute_window() -> None:
    limiter = EndpointRateLimiter(endpoint="tiktok:research:user_info", limit=120, remaining=120)
    assert not limiter.is_limited
    assert limiter.remaining == 120

    future_reset = time.time() + 60.0
    headers = {
        "x-rate-limit-limit": "120",
        "x-rate-limit-remaining": "0",
        "x-rate-limit-reset": str(future_reset),
    }
    limiter.update_from_headers(headers)
    assert limiter.remaining == 0
    assert limiter.is_limited

    with pytest.raises(RateLimitExceededError) as exc_info:
        limiter.check_or_raise(platform="tiktok")
    assert exc_info.value.retry_after_seconds > 0
