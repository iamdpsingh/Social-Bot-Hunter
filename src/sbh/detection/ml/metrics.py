"""Metrics computation, probability calibration curves, and error calibration diagnostics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

try:
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
except ImportError:
    accuracy_score = None  # type: ignore[assignment]
    auc = None  # type: ignore[assignment]
    brier_score_loss = None  # type: ignore[assignment]
    confusion_matrix = None  # type: ignore[assignment]
    f1_score = None  # type: ignore[assignment]
    log_loss = None  # type: ignore[assignment]
    precision_recall_curve = None  # type: ignore[assignment]
    precision_score = None  # type: ignore[assignment]
    recall_score = None  # type: ignore[assignment]
    roc_auc_score = None  # type: ignore[assignment]


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
        mask = (y_p >= low) & (y_p <= high) if i == n_bins - 1 else (y_p >= low) & (y_p < high)

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


def compute_evaluation_metrics(
    y_true: np.ndarray | list[int],
    y_pred: np.ndarray | list[int],
    y_prob: np.ndarray | list[float],
    n_bins: int = 10,
) -> EvaluationMetrics:
    """Compute comprehensive suite of performance, calibration, and classification metrics."""
    y_t = np.asarray(y_true, dtype=np.int32)
    y_p = np.asarray(y_pred, dtype=np.int32)
    y_pr = np.clip(np.asarray(y_prob, dtype=np.float64), 1e-15, 1.0 - 1e-15)

    prec = float(precision_score(y_t, y_p, zero_division=0.0))
    rec = float(recall_score(y_t, y_p, zero_division=0.0))
    f1 = float(f1_score(y_t, y_p, zero_division=0.0))
    acc = float(accuracy_score(y_t, y_p))
    brier = float(brier_score_loss(y_t, y_pr))
    ll = float(log_loss(y_t, y_pr, labels=[0, 1]))
    ece = compute_expected_calibration_error(y_t, y_pr, n_bins)

    # ROC-AUC and PR-AUC require at least 2 distinct classes in ground truth
    unique_classes = np.unique(y_t)
    if len(unique_classes) > 1:
        roc_val = float(roc_auc_score(y_t, y_pr))
        p_curve, r_curve, _ = precision_recall_curve(y_t, y_pr)
        pr_val = float(auc(r_curve, p_curve))
    else:
        roc_val = 0.5
        pr_val = 0.0

    # Confusion matrix
    cm = confusion_matrix(y_t, y_p, labels=[0, 1])
    cm_dict = {
        "tn": int(cm[0, 0]),
        "fp": int(cm[0, 1]),
        "fn": int(cm[1, 0]),
        "tp": int(cm[1, 1]),
    }

    return EvaluationMetrics(
        precision=round(prec, 4),
        recall=round(rec, 4),
        f1=round(f1, 4),
        pr_auc=round(pr_val, 4),
        roc_auc=round(roc_val, 4),
        brier_score=round(brier, 4),
        ece=round(ece, 4),
        accuracy=round(acc, 4),
        log_loss_value=round(ll, 4),
        confusion_matrix=cm_dict,
    )


def metrics_to_summary_dict(m: EvaluationMetrics) -> dict[str, Any]:
    """Serialize evaluation metrics into JSON-compatible dictionary."""
    return {
        "precision": m.precision,
        "recall": m.recall,
        "f1": m.f1,
        "pr_auc": m.pr_auc,
        "roc_auc": m.roc_auc,
        "brier_score": m.brier_score,
        "ece": m.ece,
        "accuracy": m.accuracy,
        "log_loss": m.log_loss_value,
        "confusion_matrix": m.confusion_matrix,
    }
