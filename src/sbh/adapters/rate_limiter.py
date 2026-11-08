"""Rate limiting and backoff window management for platform APIs."""

from __future__ import annotations

import contextlib
import time
from dataclasses import dataclass

from sbh.adapters.errors import RateLimitExceededError


@dataclass
class EndpointRateLimiter:
    """Tracks endpoint rate limit headers and calculates backoff intervals."""

    endpoint: str
    limit: int = 15
    remaining: int = 15
    reset_epoch: float = 0.0

    @property
    def is_limited(self) -> bool:
        if self.remaining <= 0:
            return time.time() < self.reset_epoch
        return False

    @property
    def seconds_until_reset(self) -> float:
        now = time.time()
        return max(0.0, self.reset_epoch - now)

    def update_from_headers(self, headers: dict[str, str]) -> None:
        """Update limit, remaining and reset time from HTTP response headers."""
        limit_val = headers.get("x-rate-limit-limit")
        rem_val = headers.get("x-rate-limit-remaining")
        reset_val = headers.get("x-rate-limit-reset")

        if limit_val and limit_val.isdigit():
            self.limit = int(limit_val)
        if rem_val and rem_val.isdigit():
            self.remaining = int(rem_val)
        if reset_val and (reset_val.isdigit() or "." in reset_val):
            with contextlib.suppress(ValueError):
                self.reset_epoch = float(reset_val)

    def check_or_raise(self, platform: str = "x") -> None:
        """Raise RateLimitExceededError if limit is exhausted and reset is pending."""
        if self.is_limited:
            raise RateLimitExceededError(
                f"Rate limit exceeded for endpoint {self.endpoint}. "
                f"Reset in {self.seconds_until_reset:.1f}s",
                platform=platform,
                retry_after_seconds=self.seconds_until_reset,
                endpoint=self.endpoint,
            )
