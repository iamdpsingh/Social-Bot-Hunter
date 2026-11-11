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


class ClusterGroupSplitter:
    """Group-aware cross-validation splitter preventing cluster / botnet data leakage.

    Guarantees:
        train_groups intersection test_groups is strictly empty.
    """

    def __init__(self, n_splits: int = 5, shuffle: bool = True, random_state: int = 42) -> None:
        self.n_splits = n_splits
        self.splitter = StratifiedGroupKFold(n_splits=n_splits, shuffle=shuffle, random_state=random_state)

    def split(
        self,
        X: np.ndarray | list[list[float]],
        y: np.ndarray | list[int],
        groups: np.ndarray | list[str | int],
    ):
        x_arr = np.asarray(X)
        y_arr = np.asarray(y)
        g_arr = np.asarray(groups)

        for train_idx, test_idx in self.splitter.split(x_arr, y_arr, g_arr):
            # Assert zero leakage contract
            train_g = set(g_arr[train_idx])
            test_g = set(g_arr[test_idx])
            if train_g & test_g:
                raise ValueError(f"Data leakage detected! Shared groups: {train_g & test_g}")
            yield train_idx, test_idx


class TemporalSplitter:
    """Chronological train/test splitter ensuring evaluation mimics live forward deployment."""

    def __init__(self, cutoff_time: datetime) -> None:
        self.cutoff_time = cutoff_time

    def split(self, timestamps: list[datetime]) -> tuple[list[int], list[int]]:
        train_indices: list[int] = []
        test_indices: list[int] = []

        for idx, ts in enumerate(timestamps):
            if ts < self.cutoff_time:
                train_indices.append(idx)
            else:
                test_indices.append(idx)

        if not train_indices or not test_indices:
            raise ValueError(f"Temporal cutoff {self.cutoff_time} resulted in empty train or test split.")

        return train_indices, test_indices
