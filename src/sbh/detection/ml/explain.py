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
