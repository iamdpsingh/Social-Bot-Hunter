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


class ModelExplainer:
    """Calculates local feature attributions and global feature importances."""

    def __init__(self, feature_names: tuple[str, ...] | None = None) -> None:
        self.feature_names = feature_names or ALL_FEATURE_NAMES

    def explain_prediction(
        self,
        account_id: str,
        feature_vector: list[float],
        model: Any,
        top_k: int = 5,
    ) -> PredictionExplanation:
        prob = float(model.predict_proba([feature_vector])[0])
        band = determine_risk_band(prob)

        # Compute attributions
        attributions = self._compute_attributions(feature_vector, model)

        positive = [a for a in attributions if a.contribution > 0]
        negative = [a for a in attributions if a.contribution < 0]

        positive_sorted = sorted(positive, key=lambda a: abs(a.contribution), reverse=True)[:top_k]
        negative_sorted = sorted(negative, key=lambda a: abs(a.contribution), reverse=True)[:top_k]

        global_imps = self.get_global_importances(model)
        missing_count = sum(1 for a in attributions if a.is_missing)

        return PredictionExplanation(
            account_id=account_id,
            bot_probability=round(prob, 4),
            risk_band=band,
            top_positive_drivers=positive_sorted,
            top_negative_drivers=negative_sorted,
            global_feature_importances=global_imps,
            missing_feature_count=missing_count,
        )

    def _compute_attributions(self, feature_vector: list[float], model: Any) -> list[FeatureAttribution]:
        """Extract signed feature contributions based on model architecture."""
        attributions: list[FeatureAttribution] = []
        vec = np.asarray(feature_vector, dtype=np.float64)

        # 1. CalibratedClassifierCV
        underlying = getattr(model, "calibrator", None) or getattr(model, "clf", model)
        if hasattr(underlying, "calibrated_classifiers_"):
            # Ensemble of calibrated folds
            base_estimator = underlying.calibrated_classifiers_[0].estimator
        else:
            base_estimator = underlying

        # 2. Linear models (coefficients)
        if hasattr(base_estimator, "coef_"):
            coefs = base_estimator.coef_[0]
            raw_contribs = coefs * vec
            total_abs = np.sum(np.abs(raw_contribs)) or 1.0
            weights = raw_contribs / total_abs

            for i, name in enumerate(self.feature_names):
                is_miss = bool(i >= len(CORE_FEATURE_NAMES) and vec[i] == 1.0)
                val = float(vec[i])
                contrib = float(raw_contribs[i])
                w = float(weights[i])
                desc = describe_feature_impact(name, val, contrib > 0, is_miss)
                attributions.append(
                    FeatureAttribution(
                        feature_name=name,
                        feature_value=round(val, 4),
                        contribution=round(contrib, 4),
                        relative_weight=round(w, 4),
                        is_missing=is_miss,
                        explanation=desc,
                    )
                )

        # 3. Tree models (feature_importances_)
        elif hasattr(base_estimator, "feature_importances_"):
            imps = base_estimator.feature_importances_
            # Use deviation from median/zero weighted by feature importance
            for i, name in enumerate(self.feature_names):
                is_miss = bool(i >= len(CORE_FEATURE_NAMES) and vec[i] == 1.0)
                val = float(vec[i])
                imp = float(imps[i])
                # Heuristic directional contribution
                direction = 1.0 if val > 0 else -1.0
                contrib = imp * direction
                desc = describe_feature_impact(name, val, contrib > 0, is_miss)
                attributions.append(
                    FeatureAttribution(
                        feature_name=name,
                        feature_value=round(val, 4),
                        contribution=round(contrib, 4),
                        relative_weight=round(imp, 4),
                        is_missing=is_miss,
                        explanation=desc,
                    )
                )

        else:
            # Fallback uniform attribution
            for i, name in enumerate(self.feature_names):
                val = float(vec[i])
                attributions.append(
                    FeatureAttribution(
                        feature_name=name,
                        feature_value=round(val, 4),
                        contribution=0.0,
                        relative_weight=0.0,
                        is_missing=False,
                        explanation=f"{name}: Neutral contribution.",
                    )
                )

        return attributions

    def get_global_importances(self, model: Any) -> dict[str, float]:
        """Extract global feature importance mapping."""
        underlying = getattr(model, "calibrator", None) or getattr(model, "clf", model)
        if hasattr(underlying, "calibrated_classifiers_"):
            base_estimator = underlying.calibrated_classifiers_[0].estimator
        else:
            base_estimator = underlying

        if hasattr(base_estimator, "feature_importances_"):
            imps = base_estimator.feature_importances_
            pairs = sorted(zip(self.feature_names, imps, strict=False), key=lambda x: x[1], reverse=True)
            return {name: round(float(v), 4) for name, v in pairs}

        if hasattr(base_estimator, "coef_"):
            coefs = np.abs(base_estimator.coef_[0])
            total = np.sum(coefs) or 1.0
            norm = coefs / total
            pairs = sorted(zip(self.feature_names, norm, strict=False), key=lambda x: x[1], reverse=True)
            return {name: round(float(v), 4) for name, v in pairs}

        return {}


def explanation_to_dict(exp: PredictionExplanation) -> dict[str, Any]:
    """Convert PredictionExplanation into JSON-serializable dictionary."""
    return {
        "account_id": exp.account_id,
        "bot_probability": exp.bot_probability,
        "risk_band": exp.risk_band,
        "top_positive_drivers": [
            {
                "feature_name": a.feature_name,
                "feature_value": a.feature_value,
                "contribution": a.contribution,
                "relative_weight": a.relative_weight,
                "is_missing": a.is_missing,
                "explanation": a.explanation,
            }
            for a in exp.top_positive_drivers
        ],
        "top_negative_drivers": [
            {
                "feature_name": a.feature_name,
                "feature_value": a.feature_value,
                "contribution": a.contribution,
                "relative_weight": a.relative_weight,
                "is_missing": a.is_missing,
                "explanation": a.explanation,
            }
            for a in exp.top_negative_drivers
        ],
        "global_feature_importances": exp.global_feature_importances,
        "missing_feature_count": exp.missing_feature_count,
    }


def format_text_explanation(exp: PredictionExplanation) -> str:
    """Produce human-friendly CLI string detailing key drivers."""
    lines = [
        f"Prediction for account '{exp.account_id}': {exp.bot_probability:.1%} ({exp.risk_band.upper()})",
        "",
        "Top Risk Drivers (pushing towards Bot):",
    ]
    for d in exp.top_positive_drivers:
        lines.append(f"  + {d.feature_name} = {d.feature_value:.3g} ({d.explanation})")

    if exp.top_negative_drivers:
        lines.append("")
        lines.append("Top Organic Signals (pushing towards Benign):")
        for d in exp.top_negative_drivers:
            lines.append(f"  - {d.feature_name} = {d.feature_value:.3g} ({d.explanation})")

    return "\n".join(lines)
