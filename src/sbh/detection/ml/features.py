"""Account and content feature extraction with missingness handling."""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from sbh.detection.simhash import compute_simhash, hamming_distance

CORE_FEATURE_NAMES: tuple[str, ...] = (
    "account_age_days",
    "followers_count",
    "following_count",
    "follower_following_ratio",
    "log_follower_ratio",
    "has_default_profile_image",
    "screen_name_length",
    "screen_name_digits",
    "screen_name_digit_ratio",
    "screen_name_entropy",
    "description_length",
    "description_has_url",
    "description_uppercase_ratio",
    "statuses_count",
    "post_frequency_per_day",
    "mean_inter_post_time_sec",
    "std_inter_post_time_sec",
    "hourly_entropy",
    "simhash_max_cluster_size",
    "simhash_duplicate_ratio",
    "url_post_ratio",
    "mention_post_ratio",
)

INDICATOR_FEATURE_NAMES: tuple[str, ...] = tuple(f"is_missing_{f}" for f in CORE_FEATURE_NAMES)
ALL_FEATURE_NAMES: tuple[str, ...] = CORE_FEATURE_NAMES + INDICATOR_FEATURE_NAMES


@dataclass
class AccountFeatureVector:
    """Extracted raw feature values for an account, with optional None for missing."""

    account_id: str
    features: dict[str, float | None] = field(default_factory=dict)
    extracted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def get(self, name: str, default: float | None = None) -> float | None:
        return self.features.get(name, default)


def calculate_shannon_entropy(text: str) -> float:
    """Compute Shannon entropy in bits for an input string."""
    if not text:
        return 0.0
    length = len(text)
    counts = Counter(text)
    entropy = 0.0
    for count in counts.values():
        p = count / length
        entropy -= p * math.log2(p)
    return round(entropy, 4)


def calculate_hourly_entropy(timestamps: list[datetime]) -> float:
    """Compute normalized entropy of activity across 24 hours of the day [0.0, 1.0]."""
    if not timestamps:
        return 0.0
    hours = [dt.hour for dt in timestamps]
    counts = Counter(hours)
    n = len(timestamps)
    entropy = 0.0
    for count in counts.values():
        p = count / n
        entropy -= p * math.log2(p)
    # Normalized by max entropy log2(24) ~ 4.58496 bits
    max_entropy = math.log2(24)
    normalized = entropy / max_entropy if max_entropy > 0 else 0.0
    return round(min(1.0, max(0.0, normalized)), 4)


def calculate_inter_post_intervals(timestamps: list[datetime]) -> tuple[float | None, float | None]:
    """Calculate mean and standard deviation of inter-post arrival times in seconds."""
    if len(timestamps) < 2:
        return None, None
    sorted_ts = sorted(timestamps)
    intervals: list[float] = []
    for i in range(1, len(sorted_ts)):
        delta = (sorted_ts[i] - sorted_ts[i - 1]).total_seconds()
        if delta >= 0:
            intervals.append(delta)
    if not intervals:
        return None, None
    mean_val = sum(intervals) / len(intervals)
    variance = sum((x - mean_val) ** 2 for x in intervals) / len(intervals)
    std_val = math.sqrt(variance)
    return round(mean_val, 2), round(std_val, 2)
