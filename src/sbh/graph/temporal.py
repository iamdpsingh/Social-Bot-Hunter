"""Temporal synchronisation between accounts' posting times."""

from __future__ import annotations

from bisect import bisect_left
from dataclasses import dataclass
from itertools import combinations


@dataclass(frozen=True)
class SyncResult:
    observed: int  # posts with a post by another member within +-window
    expected: float  # expectation if every member posted at uniformly random times
    lift: float | None
    members_used: int
    span_seconds: float
    note: str | None = None


def _count_within(a: list[float], b: list[float], w: float) -> int:
    """Posts in sorted list ``a`` that have a post in sorted list ``b`` within +-w seconds."""
    n = 0
    for t in a:
        lo = bisect_left(b, t - w)
        if lo < len(b) and b[lo] <= t + w:
            n += 1
    return n


def sync_lift(posts_by_member: dict[str, list[float]], window: float, min_posts: int) -> SyncResult:
    """Observed vs. expected cross-member co-posting within +-``window`` seconds.

    Baseline: if member b posts ``n_b`` times at uniformly random moments over the common
    observation span T, a given post of member a has a b-post within the window with
    probability ~ min(1, n_b * 2w / T). Real posting is not uniform (people sleep), so
    organic accounts can show lift above 1; the threshold in config is set well above that and
    this is documented as a limitation. Members with fewer than ``min_posts`` posts are ignored.
    """
    used = {m: sorted(ts) for m, ts in posts_by_member.items() if len(ts) >= min_posts}
    if len(used) < 2:
        return SyncResult(0, 0.0, None, len(used), 0.0, "fewer than two members with enough posts")
    all_ts = [t for ts in used.values() for t in ts]
    span = max(all_ts) - min(all_ts)
    if span <= 0:
        return SyncResult(0, 0.0, None, len(used), 0.0, "all posts share one timestamp")
    observed, expected = 0, 0.0
    for a, b in combinations(sorted(used), 2):
        ta, tb = used[a], used[b]
        observed += _count_within(ta, tb, window) + _count_within(tb, ta, window)
        expected += len(ta) * min(1.0, len(tb) * 2 * window / span)
        expected += len(tb) * min(1.0, len(ta) * 2 * window / span)
    lift = observed / expected if expected > 0 else None
    return SyncResult(observed, expected, lift, len(used), span)

