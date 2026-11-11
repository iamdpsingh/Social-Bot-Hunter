"""Metrics computation, probability calibration curves, and error calibration diagnostics."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    auc,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)


@dataclass
class EvaluationMetrics:
    """Standardized multi-metric evaluation summary."""

    precision: float
    recall: float
    f1: float
    pr_auc: float
    roc_auc: float
    brier_score: float
    ece: float  # Expected Calibration Error
    accuracy: float
    log_loss_value: float
    confusion_matrix: dict[str, int] = field(default_factory=dict)


@dataclass
class CalibrationCurvePoint:
    """Coordinate point for reliability diagrams."""

    bin_index: int
    mean_predicted_prob: float
    fraction_positives: float
    sample_count: int


def compute_calibration_curve(
    y_true: np.ndarray | list[int],
    y_prob: np.ndarray | list[float],
    n_bins: int = 10,
) -> list[CalibrationCurvePoint]:
    """Calculate reliability diagram coordinates across equal-width probability bins [0, 1]."""
    y_t = np.asarray(y_true, dtype=np.int32)
    y_p = np.asarray(y_prob, dtype=np.float64)

    bins = np.linspace(0.0, 1.0, n_bins + 1)
    points: list[CalibrationCurvePoint] = []

    for i in range(n_bins):
        low, high = bins[i], bins[i + 1]
        # Include high boundary for the last bin
        if i == n_bins - 1:
            mask = (y_p >= low) & (y_p <= high)
        else:
            mask = (y_p >= low) & (y_p < high)

        count = int(np.sum(mask))
        if count > 0:
            mean_prob = float(np.mean(y_p[mask]))
            frac_pos = float(np.mean(y_t[mask]))
        else:
            mean_prob = float((low + high) / 2.0)
            frac_pos = 0.0

        points.append(
            CalibrationCurvePoint(
                bin_index=i,
                mean_predicted_prob=round(mean_prob, 4),
                fraction_positives=round(frac_pos, 4),
                sample_count=count,
            )
        )
    return points


def compute_expected_calibration_error(
    y_true: np.ndarray | list[int],
    y_prob: np.ndarray | list[float],
    n_bins: int = 10,
) -> float:
    """Compute Expected Calibration Error (ECE): weighted average gap between confidence and accuracy."""
    points = compute_calibration_curve(y_true, y_prob, n_bins)
    total_samples = sum(p.sample_count for p in points)
    if total_samples == 0:
        return 0.0

    ece = 0.0
    for p in points:
        if p.sample_count > 0:
            gap = abs(p.fraction_positives - p.mean_predicted_prob)
            ece += (p.sample_count / total_samples) * gap
    return round(float(ece), 4)
