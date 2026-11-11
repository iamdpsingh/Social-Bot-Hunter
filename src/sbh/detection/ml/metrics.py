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
