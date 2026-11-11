"""Explainability and local feature attribution engine for ML bot predictions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from sbh.detection.ml.features import ALL_FEATURE_NAMES, CORE_FEATURE_NAMES
from sbh.detection.ml.models import determine_risk_band


@dataclass
class FeatureAttribution:
    """Individual feature contribution to a model prediction."""

    feature_name: str
    feature_value: float
    contribution: float  # Positive = bot risk, negative = human/organic indicator
    relative_weight: float
    is_missing: bool
    explanation: str


@dataclass
class PredictionExplanation:
    """Complete explainability report for an individual prediction."""

    account_id: str
    bot_probability: float
    risk_band: str
    top_positive_drivers: list[FeatureAttribution] = field(default_factory=list)
    top_negative_drivers: list[FeatureAttribution] = field(default_factory=list)
    global_feature_importances: dict[str, float] = field(default_factory=dict)
    missing_feature_count: int = 0


FEATURE_DESCRIPTIONS: dict[str, tuple[str, str]] = {
    "simhash_duplicate_ratio": (
        "High volume of near-duplicate copy-pasted posts",
        "Diverse, unique post content without robotic repetition",
    ),
    "hourly_entropy": (
        "Concentrated bursts of activity lacking human sleep cycles",
        "Organic diurnal rhythm spread across active hours",
    ),
    "screen_name_entropy": (
        "High character randomness in username indicative of generator scripts",
        "Natural, pronounceable username pattern",
    ),
    "follower_following_ratio": (
        "Severely asymmetric following pattern common in follow-churn bots",
        "Balanced, organic community network ratio",
    ),
    "mean_inter_post_time_sec": (
        "Robotic regular inter-post timing intervals",
        "Natural, stochastic intervals between social posts",
    ),
    "url_post_ratio": (
        "Heavy concentration of outbound promotional and redirect URLs",
        "Healthy mix of conversational posts without external links",
    ),
    "has_default_profile_image": (
        "Default placeholder avatar indicating unpersonalized account",
        "Custom uploaded profile avatar",
    ),
    "account_age_days": (
        "Recently created disposable account",
        "Mature, established account history",
    ),
}


def describe_feature_impact(name: str, value: float, is_positive: bool, is_missing: bool) -> str:
    """Produce human-auditable text explanation of an indicator's impact."""
    if is_missing:
        return f"{name}: Data was unavailable for this profile; missingness accounted for."
    desc_pair = FEATURE_DESCRIPTIONS.get(name)
    if desc_pair:
        return desc_pair[0] if is_positive else desc_pair[1]
    dir_str = "increases bot risk" if is_positive else "indicates organic activity"
    return f"{name} ({value:.3g}) {dir_str}."
