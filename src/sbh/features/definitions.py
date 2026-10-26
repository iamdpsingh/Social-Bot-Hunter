"""Feature catalogue and result type. Bump FEATURE_VERSION when any definition changes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

FEATURE_VERSION = "features-v1"

# name -> category. Data-quality features describe the evidence, not the account: they carry
# no scoring weight and exist so coverage and freshness are visible next to every score.
CATALOGUE: dict[str, str] = {
    "following_follower_ratio": "network",
    "profile_completeness": "profile",
    "username_digit_ratio": "profile",
    "post_rate_per_day": "behavioural",
    "post_interval_cv": "behavioural",
    "duplicate_content_ratio": "behavioural",
    "follower_growth_spike": "network",
    "max_following_jaccard": "network",
    "reciprocity_ratio": "network",
    "observation_age_days": "data_quality",
    "field_availability": "data_quality",
    "observation_count": "data_quality",
    "relationship_coverage": "data_quality",
    "posts_observed": "data_quality",
}


@dataclass(frozen=True)
class FeatureResult:
    """``value is None`` means *unavailable*; it never means zero."""

    name: str
    value: float | None
    unavailable_reason: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def category(self) -> str:
        return CATALOGUE[self.name]

    @staticmethod
    def ok(name: str, value: float, **details: Any) -> FeatureResult:
        return FeatureResult(name, float(value), None, details)

    @staticmethod
    def unavailable(name: str, reason: str, **details: Any) -> FeatureResult:
        return FeatureResult(name, None, reason, details)
