"""Cross-validation and zero-leakage evaluation splitting mechanisms."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import numpy as np
from sklearn.model_selection import StratifiedGroupKFold

from sbh.detection.ml.metrics import EvaluationMetrics, compute_evaluation_metrics
from sbh.detection.ml.models import BotModelProtocol


@dataclass
class CrossValidationResult:
    """Aggregated evaluation across disjoint group-aware cross-validation folds."""

    fold_metrics: list[EvaluationMetrics] = field(default_factory=list)
    mean_precision: float = 0.0
    mean_recall: float = 0.0
    mean_f1: float = 0.0
    mean_pr_auc: float = 0.0
    mean_roc_auc: float = 0.0
    mean_brier: float = 0.0
    mean_ece: float = 0.0
    std_f1: float = 0.0
