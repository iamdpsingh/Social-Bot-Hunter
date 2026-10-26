"""Bounded retry with exponential backoff and jitter.

Live platform adapters (Phase 5+) must use this for transient failures. Permanent
failures (permission denied, unsupported operation) are never retried.
"""

from __future__ import annotations

import logging
import random
import time
from collections.abc import Callable
from typing import TypeVar

from sbh.shared.errors import PermanentError, TransientError

T = TypeVar("T")
log = logging.getLogger(__name__)


def retry_with_backoff(
    fn: Callable[[], T],
    *,
    max_attempts: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    sleep: Callable[[float], None] = time.sleep,
    rng: random.Random | None = None,
) -> T:
    """Call ``fn`` until it succeeds, a permanent error occurs, or attempts are exhausted.

    Delay uses "full jitter": uniform(0, min(max_delay, base * 2**attempt)). When the
    platform supplies retry guidance (``TransientError.retry_after``) that value is
    honoured as a lower bound, still capped by ``max_delay``.
    """
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")
    rng = rng or random.Random()
    for attempt in range(max_attempts):
        try:
            return fn()
        except PermanentError:
            raise
        except TransientError as exc:
            if attempt == max_attempts - 1:
                raise
            backoff = rng.uniform(0, min(max_delay, base_delay * (2**attempt)))
            delay = min(max_delay, max(backoff, exc.retry_after or 0.0))
            log.warning("transient failure, retrying", extra={"attempt": attempt + 1, "delay": delay})
            sleep(delay)
    raise AssertionError("unreachable")  # pragma: no cover
