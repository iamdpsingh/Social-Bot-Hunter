"""Cross-validation and zero-leakage evaluation splitting mechanisms."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import numpy as np
from sklearn.model_selection import StratifiedGroupKFold

from sbh.detection.ml.metrics import EvaluationMetrics, compute_evaluation_metrics


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
    ) -> Iterator[tuple[np.ndarray, np.ndarray]]:
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


def run_cluster_cross_validation(
    model_factory: Any,
    X: np.ndarray | list[list[float]],
    y: np.ndarray | list[int],
    groups: np.ndarray | list[str | int],
    n_splits: int = 5,
) -> CrossValidationResult:
    """Execute k-fold cluster-aware cross validation and aggregate performance metrics."""
    x_arr = np.asarray(X, dtype=np.float64)
    y_arr = np.asarray(y, dtype=np.int32)
    splitter = ClusterGroupSplitter(n_splits=n_splits)

    fold_metrics: list[EvaluationMetrics] = []

    for train_idx, test_idx in splitter.split(x_arr, y_arr, groups):
        x_train, y_train = x_arr[train_idx], y_arr[train_idx]
        x_test, y_test = x_arr[test_idx], y_arr[test_idx]

        model = model_factory()
        model.fit(x_train, y_train)

        y_prob = model.predict_proba(x_test)
        y_pred = model.predict(x_test)

        metrics = compute_evaluation_metrics(y_test, y_pred, y_prob)
        fold_metrics.append(metrics)

    precisions = [m.precision for m in fold_metrics]
    recalls = [m.recall for m in fold_metrics]
    f1s = [m.f1 for m in fold_metrics]
    pr_aucs = [m.pr_auc for m in fold_metrics]
    roc_aucs = [m.roc_auc for m in fold_metrics]
    briers = [m.brier_score for m in fold_metrics]
    eces = [m.ece for m in fold_metrics]

    return CrossValidationResult(
        fold_metrics=fold_metrics,
        mean_precision=round(float(np.mean(precisions)), 4),
        mean_recall=round(float(np.mean(recalls)), 4),
        mean_f1=round(float(np.mean(f1s)), 4),
        mean_pr_auc=round(float(np.mean(pr_aucs)), 4),
        mean_roc_auc=round(float(np.mean(roc_aucs)), 4),
        mean_brier=round(float(np.mean(briers)), 4),
        mean_ece=round(float(np.mean(eces)), 4),
        std_f1=round(float(np.std(f1s)), 4),
    )
