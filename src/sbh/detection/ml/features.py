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
