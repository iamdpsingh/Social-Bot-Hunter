"""Explainable rules-based risk score.

    R = 100 * sum(w_i * e_i) / sum(w_i)       over rules whose feature is available

e_i in [0, 1] comes from a linear ramp (zero_at -> 0, full_at -> 1). Unavailable features are
excluded from both sums and reported as lost coverage. When too little evidence is available
the result is ``insufficient_evidence`` with no score: a number is never manufactured.

The score is a heuristic indicator, not a probability and not proof of automation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sbh.config import BandSpec, RuleSpec, ScoringConfig
from sbh.features.definitions import FeatureResult

GENERIC_LIMITATION = (
    "Heuristic indicator derived from observable signals. It is not a probability, not a verified "
    "fake-account percentage, and not proof that the account is automated."
)


def evidence_value(rule: RuleSpec, value: float) -> float:
    """Map a raw feature value onto [0, 1] using the rule's ramp."""
    e = (value - rule.zero_at) / (rule.full_at - rule.zero_at)
    return min(1.0, max(0.0, e))


def band_for(score: float, bands: tuple[BandSpec, ...]) -> str:
    label = bands[0].label
    for b in bands:
        if score >= b.lower:
            label = b.label
    return label


@dataclass(frozen=True)
class AssessmentResult:
    status: str  # 'scored' | 'insufficient_evidence'
    score: float | None
    band: str | None
    evidence_coverage: float  # available weight / total weight
    features_available: int
    features_total: int
    contributions: list[dict[str, Any]] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)


def score_account(features: dict[str, FeatureResult], cfg: ScoringConfig) -> AssessmentResult:
    total_w = sum(r.weight for r in cfg.rules)
    available: list[tuple[RuleSpec, FeatureResult, float]] = []
    contributions: list[dict[str, Any]] = []
    limitations: list[str] = [GENERIC_LIMITATION]

    for rule in cfg.rules:
        feat = features.get(rule.feature)
        if feat is None or feat.value is None:
            reason = feat.unavailable_reason if feat else "feature was not computed"
            contributions.append({"feature": rule.feature, "available": False, "weight": rule.weight,
                                  "reason": reason})
            limitations.append(f"{rule.feature} unavailable: {reason}")
            continue
        e = evidence_value(rule, feat.value)
        available.append((rule, feat, e))
        contributions.append({"feature": rule.feature, "available": True, "value": feat.value,
                              "evidence": round(e, 6), "weight": rule.weight, "details": feat.details})

    avail_w = sum(r.weight for r, _, _ in available)
    coverage = avail_w / total_w if total_w else 0.0
    n_avail, n_total = len(available), len(cfg.rules)

    if n_avail < cfg.min_features or coverage < cfg.min_weight_coverage:
        limitations.append(
            f"Insufficient evidence: {n_avail}/{n_total} rules available (need at least "
            f"{cfg.min_features}) and {coverage:.0%} weight coverage (need {cfg.min_weight_coverage:.0%}). "
            "No score is reported.")
        return AssessmentResult("insufficient_evidence", None, None, round(coverage, 6), n_avail, n_total,
                                contributions, limitations)

    raw = 100.0 * sum(r.weight * e for r, _, e in available) / avail_w
    score = round(raw, 2)
    for c in contributions:
        if c["available"]:
            c["points"] = round(100.0 * c["weight"] * c["evidence"] / avail_w, 4)
    if coverage < 1.0:
        limitations.append(f"Score is based on {coverage:.0%} of the configured evidence weight.")
    return AssessmentResult("scored", score, band_for(score, cfg.bands), round(coverage, 6), n_avail,
                            n_total, contributions, limitations)


def evidence_summary(contribution: dict[str, Any], rule: RuleSpec) -> str:
    """One readable line explaining a contributing indicator (used for evidence records)."""
    v = contribution["value"]
    return (f"{rule.feature} = {v:.3g} maps to evidence {contribution['evidence']:.2f} "
            f"(weight {rule.weight:g}, {contribution['points']:.1f} score points). {rule.description}")
