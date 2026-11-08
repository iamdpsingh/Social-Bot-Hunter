"""Tests for EndpointRateLimiter behavior."""

from __future__ import annotations

import time

import pytest

from sbh.adapters.errors import RateLimitExceededError
from sbh.adapters.rate_limiter import EndpointRateLimiter


def test_rate_limiter_initial_state() -> None:
    limiter = EndpointRateLimiter(endpoint="/2/users/by/username")
    assert not limiter.is_limited
    assert limiter.remaining == 15
    limiter.check_or_raise()


def test_rate_limiter_update_headers() -> None:
    limiter = EndpointRateLimiter(endpoint="/2/users/:id/followers")
    future_reset = time.time() + 300.0
    headers = {
        "x-rate-limit-limit": "15",
        "x-rate-limit-remaining": "0",
        "x-rate-limit-reset": str(future_reset),
    }
    limiter.update_from_headers(headers)
    assert limiter.remaining == 0
    assert limiter.is_limited
    assert limiter.seconds_until_reset > 0

    with pytest.raises(RateLimitExceededError) as exc_info:
        limiter.check_or_raise(platform="x")
    assert exc_info.value.retry_after_seconds > 0
