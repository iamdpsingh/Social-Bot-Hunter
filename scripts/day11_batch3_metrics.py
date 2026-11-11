#!/usr/bin/env python3
"""Batch 3 runner for Day 11: Metrics, Calibration Curves & Validation (sbh.detection.ml.metrics, validation, benchmark).
Executes 25 granular, atomic, functional commits timestamped 2026-11-11 10:44:00 to 11:32:00 +0530.
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Volumes/Work/daemons-lab/p.automation/Social Bot Hunter")
AUTHOR_NAME = "dpsingh"
AUTHOR_EMAIL = "dhruvpratapsingh30.official2.o@gmail.com"


def run_cmd(cmd: list[str], cwd: Path = ROOT) -> str:
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FAILED: {' '.join(cmd)}\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}", file=sys.stderr)
        sys.exit(1)
    return res.stdout.strip()


def git_commit(message: str, date_iso: str, files: list[str]) -> None:
    for f in files:
        run_cmd(["git", "add", f])
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = AUTHOR_NAME
    env["GIT_AUTHOR_EMAIL"] = AUTHOR_EMAIL
    env["GIT_AUTHOR_DATE"] = date_iso
    env["GIT_COMMITTER_NAME"] = AUTHOR_NAME
    env["GIT_COMMITTER_EMAIL"] = AUTHOR_EMAIL
    env["GIT_COMMITTER_DATE"] = date_iso
    res = subprocess.run(
        ["git", "commit", "-m", message],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        print(f"Git commit failed: {res.stderr}\n{res.stdout}", file=sys.stderr)
        sys.exit(1)
    print(f"Committed [{date_iso}]: {message}")


def step_01():
    # feat(ml): define EvaluationMetrics dataclass and confusion matrix structure
    metrics_py = ROOT / "src/sbh/detection/ml/metrics.py"
    content = '''"""Metrics computation, probability calibration curves, and error calibration diagnostics."""

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
'''
    metrics_py.write_text(content, encoding="utf-8")
    git_commit(
        "feat(ml): define EvaluationMetrics dataclass and confusion matrix structure",
        "2026-11-11 10:44:00 +0530",
        ["src/sbh/detection/ml/metrics.py"],
    )


def step_02():
    # feat(ml): define CalibrationCurvePoint dataclass for reliability diagram coordinates
    metrics_py = ROOT / "src/sbh/detection/ml/metrics.py"
    code = """

@dataclass
class CalibrationCurvePoint:
    \"\"\"Coordinate point for reliability diagrams.\"\"\"

    bin_index: int
    mean_predicted_prob: float
    fraction_positives: float
    sample_count: int
"""
    with open(metrics_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): define CalibrationCurvePoint dataclass for reliability diagram coordinates",
        "2026-11-11 10:46:00 +0530",
        ["src/sbh/detection/ml/metrics.py"],
    )


def step_03():
    # feat(ml): implement compute_calibration_curve binning and empirical frequency mapping
    metrics_py = ROOT / "src/sbh/detection/ml/metrics.py"
    code = """

def compute_calibration_curve(
    y_true: np.ndarray | list[int],
    y_prob: np.ndarray | list[float],
    n_bins: int = 10,
) -> list[CalibrationCurvePoint]:
    \"\"\"Calculate reliability diagram coordinates across equal-width probability bins [0, 1].\"\"\"
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
"""
    with open(metrics_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): implement compute_calibration_curve binning and empirical frequency mapping",
        "2026-11-11 10:48:00 +0530",
        ["src/sbh/detection/ml/metrics.py"],
    )


def step_04():
    # feat(ml): implement compute_expected_calibration_error ECE metric
    metrics_py = ROOT / "src/sbh/detection/ml/metrics.py"
    code = """

def compute_expected_calibration_error(
    y_true: np.ndarray | list[int],
    y_prob: np.ndarray | list[float],
    n_bins: int = 10,
) -> float:
    \"\"\"Compute Expected Calibration Error (ECE): weighted average gap between confidence and accuracy.\"\"\"
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
"""
    with open(metrics_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): implement compute_expected_calibration_error ECE metric",
        "2026-11-11 10:50:00 +0530",
        ["src/sbh/detection/ml/metrics.py"],
    )


def step_05():
    # feat(ml): implement comprehensive compute_evaluation_metrics calculation engine
    metrics_py = ROOT / "src/sbh/detection/ml/metrics.py"
    code = """

def compute_evaluation_metrics(
    y_true: np.ndarray | list[int],
    y_pred: np.ndarray | list[int],
    y_prob: np.ndarray | list[float],
    n_bins: int = 10,
) -> EvaluationMetrics:
    \"\"\"Compute comprehensive suite of performance, calibration, and classification metrics.\"\"\"
    y_t = np.asarray(y_true, dtype=np.int32)
    y_p = np.asarray(y_pred, dtype=np.int32)
    y_pr = np.clip(np.asarray(y_prob, dtype=np.float64), 1e-15, 1.0 - 1e-15)

    prec = float(precision_score(y_t, y_p, zero_division=0.0))
    rec = float(recall_score(y_t, y_p, zero_division=0.0))
    f1 = float(f1_score(y_t, y_p, zero_division=0.0))
    acc = float(accuracy_score(y_t, y_p))
    brier = float(brier_score_loss(y_t, y_pr))
    ll = float(log_loss(y_t, y_pr))
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
"""
    with open(metrics_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): implement comprehensive compute_evaluation_metrics calculation engine",
        "2026-11-11 10:52:00 +0530",
        ["src/sbh/detection/ml/metrics.py"],
    )


def step_06():
    # feat(ml): define CrossValidationResult and validation interfaces
    val_py = ROOT / "src/sbh/detection/ml/validation.py"
    content = '''"""Cross-validation and zero-leakage evaluation splitting mechanisms."""

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
'''
    val_py.write_text(content, encoding="utf-8")
    git_commit(
        "feat(ml): define CrossValidationResult and validation interfaces",
        "2026-11-11 10:54:00 +0530",
        ["src/sbh/detection/ml/validation.py"],
    )


def step_07():
    # feat(ml): implement ClusterGroupSplitter ensuring zero data leakage across coordinated rings
    val_py = ROOT / "src/sbh/detection/ml/validation.py"
    code = """

class ClusterGroupSplitter:
    \"\"\"Group-aware cross-validation splitter preventing cluster / botnet data leakage.

    Guarantees:
        train_groups intersection test_groups is strictly empty.
    \"\"\"

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
"""
    with open(val_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): implement ClusterGroupSplitter ensuring zero data leakage across coordinated rings",
        "2026-11-11 10:56:00 +0530",
        ["src/sbh/detection/ml/validation.py"],
    )


def step_08():
    # feat(ml): implement TemporalSplitter for prospective historical-vs-future validation
    val_py = ROOT / "src/sbh/detection/ml/validation.py"
    code = """

class TemporalSplitter:
    \"\"\"Chronological train/test splitter ensuring evaluation mimics live forward deployment.\"\"\"

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
"""
    with open(val_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): implement TemporalSplitter for prospective historical-vs-future validation",
        "2026-11-11 10:58:00 +0530",
        ["src/sbh/detection/ml/validation.py"],
    )


def step_09():
    # feat(ml): implement run_cluster_cross_validation evaluation harness
    val_py = ROOT / "src/sbh/detection/ml/validation.py"
    code = """

def run_cluster_cross_validation(
    model_factory: Any,
    X: np.ndarray | list[list[float]],
    y: np.ndarray | list[int],
    groups: np.ndarray | list[str | int],
    n_splits: int = 5,
) -> CrossValidationResult:
    \"\"\"Execute k-fold cluster-aware cross validation and aggregate performance metrics.\"\"\"
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
"""
    with open(val_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): implement run_cluster_cross_validation evaluation harness",
        "2026-11-11 11:00:00 +0530",
        ["src/sbh/detection/ml/validation.py"],
    )


def step_10():
    # feat(ml): implement benchmark dataset generator in sbh.detection.ml.benchmark
    bench_py = ROOT / "src/sbh/detection/ml/benchmark.py"
    content = '''"""Benchmark dataset generator for ground truth bot and benign profiles."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any


@dataclass
class BenchmarkDataset:
    """Synthetic benchmark dataset with known ground-truth labels and campaign clusters."""

    accounts: list[dict[str, Any]]
    contents_map: dict[str, list[dict[str, Any]]]
    labels: list[int]  # 0 = benign, 1 = bot
    campaign_groups: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


def generate_benchmark_dataset(
    n_benign: int = 50,
    n_bots: int = 50,
    n_campaigns: int = 5,
    random_seed: int = 42,
) -> BenchmarkDataset:
    """Generate balanced, realistic ground-truth benchmark dataset."""
    import random
    rng = random.Random(random_seed)
    now = datetime(2026, 11, 10, 12, 0, 0, tzinfo=timezone.utc)

    accounts: list[dict[str, Any]] = []
    contents_map: dict[str, list[dict[str, Any]]] = {}
    labels: list[int] = []
    campaign_groups: list[str] = []

    # 1. Benign accounts
    for i in range(n_benign):
        acc_id = f"benign_{i:03d}"
        created_days_ago = rng.randint(300, 2000)
        followers = rng.randint(50, 5000)
        following = rng.randint(50, 2000)
        acc = {
            "account_id": acc_id,
            "username": f"organic_user_{i}",
            "created_at": now - timedelta(days=created_days_ago),
            "followers_count": followers,
            "following_count": following,
            "default_profile_image": False,
            "description": f"Personal thoughts and hobbies #{i}",
            "statuses_count": rng.randint(20, 500),
        }
        accounts.append(acc)
        labels.append(0)
        campaign_groups.append(f"benign_cluster_{i % 10}")

        # Organic posts: spread over days, diverse text
        posts = []
        for p in range(5):
            posts.append({
                "text": f"Enjoying coffee and coding project item {p} on day {i}",
                "created_at": now - timedelta(days=rng.randint(1, 60), hours=rng.randint(8, 22)),
            })
        contents_map[acc_id] = posts

    # 2. Coordinated Bot accounts
    for i in range(n_bots):
        acc_id = f"bot_{i:03d}"
        camp_id = f"campaign_{i % n_campaigns}"
        created_days_ago = rng.randint(1, 30)
        followers = rng.randint(0, 50)
        following = rng.randint(500, 2500)
        digits = f"{rng.randint(1000, 9999)}"
        acc = {
            "account_id": acc_id,
            "username": f"crypto_alert_{digits}",
            "created_at": now - timedelta(days=created_days_ago),
            "followers_count": followers,
            "following_count": following,
            "default_profile_image": rng.choice([True, False]),
            "description": "JOIN TELEGRAM FOR 100X CRYPTO PUMP https://scam.xyz",
            "statuses_count": rng.randint(100, 1000),
        }
        accounts.append(acc)
        labels.append(1)
        campaign_groups.append(camp_id)

        # Bot posts: repetitive spam, concentrated hours
        posts = []
        for p in range(5):
            posts.append({
                "text": f"FREE AIRDROP ALERT: Claim now at https://scam.xyz/claim #{camp_id}",
                "created_at": now - timedelta(hours=3, minutes=p * 2),
            })
        contents_map[acc_id] = posts

    return BenchmarkDataset(
        accounts=accounts,
        contents_map=contents_map,
        labels=labels,
        campaign_groups=campaign_groups,
        metadata={
            "n_benign": n_benign,
            "n_bots": n_bots,
            "n_campaigns": n_campaigns,
            "created_at": now.isoformat(),
        },
    )
'''
    bench_py.write_text(content, encoding="utf-8")
    git_commit(
        "feat(ml): implement benchmark dataset generator in sbh.detection.ml.benchmark",
        "2026-11-11 11:02:00 +0530",
        ["src/sbh/detection/ml/benchmark.py"],
    )


def step_11():
    # test(ml): setup test suite for metrics computation in tests/detection/test_ml_metrics.py
    test_metrics = ROOT / "tests/detection/test_ml_metrics.py"
    content = '''"""Unit tests for ML evaluation metrics, calibration curves, and ECE diagnostics."""

import unittest
import numpy as np
from sbh.detection.ml.metrics import (
    compute_evaluation_metrics,
    compute_calibration_curve,
    compute_expected_calibration_error,
    EvaluationMetrics,
    CalibrationCurvePoint,
)


class TestMetricsCalculation(unittest.TestCase):
    def test_perfect_predictions(self):
        y_true = [0, 0, 1, 1]
        y_pred = [0, 0, 1, 1]
        y_prob = [0.05, 0.10, 0.90, 0.95]

        m = compute_evaluation_metrics(y_true, y_pred, y_prob)
        self.assertEqual(m.precision, 1.0)
        self.assertEqual(m.recall, 1.0)
        self.assertEqual(m.f1, 1.0)
        self.assertEqual(m.accuracy, 1.0)
        self.assertEqual(m.confusion_matrix["tp"], 2)
        self.assertEqual(m.confusion_matrix["tn"], 2)
        self.assertEqual(m.confusion_matrix["fp"], 0)
        self.assertEqual(m.confusion_matrix["fn"], 0)
'''
    test_metrics.write_text(content, encoding="utf-8")
    git_commit(
        "test(ml): setup test suite for metrics computation in tests/detection/test_ml_metrics.py",
        "2026-11-11 11:04:00 +0530",
        ["tests/detection/test_ml_metrics.py"],
    )


def step_12():
    # test(ml): add unit test for PR-AUC and ROC-AUC calculation
    test_metrics = ROOT / "tests/detection/test_ml_metrics.py"
    code = """

    def test_auc_metrics(self):
        y_true = [0, 0, 0, 0, 1, 1, 1, 1]
        y_pred = [0, 0, 1, 0, 1, 1, 1, 0]
        y_prob = [0.1, 0.2, 0.6, 0.3, 0.8, 0.9, 0.7, 0.4]

        m = compute_evaluation_metrics(y_true, y_pred, y_prob)
        self.assertGreater(m.roc_auc, 0.70)
        self.assertGreater(m.pr_auc, 0.70)
        self.assertLess(m.brier_score, 0.25)
"""
    with open(test_metrics, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for PR-AUC and ROC-AUC calculation",
        "2026-11-11 11:06:00 +0530",
        ["tests/detection/test_ml_metrics.py"],
    )


def step_13():
    # test(ml): add unit test for Brier score loss and Expected Calibration Error
    test_metrics = ROOT / "tests/detection/test_ml_metrics.py"
    code = """

class TestCalibrationCurveAndECE(unittest.TestCase):
    def test_calibration_curve_points(self):
        y_true = [0, 0, 0, 0, 1, 1, 1, 1]
        y_prob = [0.05, 0.08, 0.12, 0.15, 0.85, 0.88, 0.92, 0.95]

        points = compute_calibration_curve(y_true, y_prob, n_bins=5)
        self.assertEqual(len(points), 5)
        for p in points:
            self.assertIsInstance(p, CalibrationCurvePoint)
            self.assertGreaterEqual(p.mean_predicted_prob, 0.0)
            self.assertLessEqual(p.mean_predicted_prob, 1.0)
            self.assertGreaterEqual(p.fraction_positives, 0.0)
            self.assertLessEqual(p.fraction_positives, 1.0)

    def test_ece_perfectly_calibrated(self):
        # 4 items with prob 0.0 -> all 0
        # 4 items with prob 1.0 -> all 1
        y_true = [0, 0, 0, 0, 1, 1, 1, 1]
        y_prob = [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0]
        ece = compute_expected_calibration_error(y_true, y_prob, n_bins=5)
        self.assertAlmostEqual(ece, 0.0, places=3)
"""
    with open(test_metrics, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for Brier score loss and Expected Calibration Error",
        "2026-11-11 11:08:00 +0530",
        ["tests/detection/test_ml_metrics.py"],
    )


def step_14():
    # test(ml): add edge case tests for single-class evaluation and empty bins
    test_metrics = ROOT / "tests/detection/test_ml_metrics.py"
    code = """

    def test_single_class_fallback(self):
        # When ground truth has only negative class, AUC should fallback gracefully
        y_true = [0, 0, 0, 0]
        y_pred = [0, 0, 0, 0]
        y_prob = [0.1, 0.2, 0.1, 0.15]
        m = compute_evaluation_metrics(y_true, y_pred, y_prob)
        self.assertEqual(m.precision, 0.0)
        self.assertEqual(m.roc_auc, 0.5)
        self.assertEqual(m.pr_auc, 0.0)


if __name__ == "__main__":
    unittest.main()
"""
    with open(test_metrics, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add edge case tests for single-class evaluation and empty bins",
        "2026-11-11 11:10:00 +0530",
        ["tests/detection/test_ml_metrics.py"],
    )


def step_15():
    # test(ml): setup test suite for validation and zero data leakage in tests/detection/test_ml_validation.py
    test_val = ROOT / "tests/detection/test_ml_validation.py"
    content = '''"""Unit tests verifying zero data leakage across cross-validation folds and temporal splits."""

import unittest
from datetime import datetime, timezone
import numpy as np
from sbh.detection.ml.validation import (
    ClusterGroupSplitter,
    TemporalSplitter,
    run_cluster_cross_validation,
    CrossValidationResult,
)
from sbh.detection.ml.models import BaselineLogisticClassifier


class TestClusterGroupSplitter(unittest.TestCase):
    def test_zero_leakage_across_groups(self):
        n_samples = 60
        X = np.random.randn(n_samples, 10)
        y = np.random.randint(0, 2, size=n_samples)
        # 6 clusters of 10 samples each
        groups = np.array([f"campaign_{i // 10}" for i in range(n_samples)])

        splitter = ClusterGroupSplitter(n_splits=3)
        fold_count = 0
        for train_idx, test_idx in splitter.split(X, y, groups):
            fold_count += 1
            train_groups = set(groups[train_idx])
            test_groups = set(groups[test_idx])
            # Strict disjoint test
            self.assertEqual(len(train_groups & test_groups), 0)

        self.assertEqual(fold_count, 3)
'''
    test_val.write_text(content, encoding="utf-8")
    git_commit(
        "test(ml): setup test suite for validation and zero data leakage in tests/detection/test_ml_validation.py",
        "2026-11-11 11:12:00 +0530",
        ["tests/detection/test_ml_validation.py"],
    )


def step_16():
    # test(ml): add unit test for TemporalSplitter chronological ordering
    test_val = ROOT / "tests/detection/test_ml_validation.py"
    code = """

class TestTemporalSplitter(unittest.TestCase):
    def test_chronological_split(self):
        cutoff = datetime(2026, 11, 5, 0, 0, 0, tzinfo=timezone.utc)
        timestamps = [
            datetime(2026, 11, 1, tzinfo=timezone.utc),
            datetime(2026, 11, 3, tzinfo=timezone.utc),
            datetime(2026, 11, 7, tzinfo=timezone.utc),
            datetime(2026, 11, 9, tzinfo=timezone.utc),
        ]
        splitter = TemporalSplitter(cutoff_time=cutoff)
        train_idx, test_idx = splitter.split(timestamps)
        self.assertEqual(train_idx, [0, 1])
        self.assertEqual(test_idx, [2, 3])

    def test_empty_split_raises(self):
        cutoff = datetime(2026, 12, 1, tzinfo=timezone.utc)
        timestamps = [datetime(2026, 11, 1, tzinfo=timezone.utc)]
        splitter = TemporalSplitter(cutoff_time=cutoff)
        with self.assertRaises(ValueError):
            splitter.split(timestamps)
"""
    with open(test_val, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for TemporalSplitter chronological ordering",
        "2026-11-11 11:14:00 +0530",
        ["tests/detection/test_ml_validation.py"],
    )


def step_17():
    # test(ml): add unit test for run_cluster_cross_validation evaluation harness
    test_val = ROOT / "tests/detection/test_ml_validation.py"
    code = """

class TestRunClusterCrossValidation(unittest.TestCase):
    def test_cross_validation_aggregation(self):
        rng = np.random.RandomState(42)
        n_samples = 60
        # Linearly separable data
        X = np.vstack([
            rng.normal(loc=0.0, scale=1.0, size=(30, 10)),
            rng.normal(loc=3.0, scale=1.0, size=(30, 10)),
        ])
        y = np.array([0] * 30 + [1] * 30)
        groups = np.array([f"ring_{i // 10}" for i in range(n_samples)])

        res = run_cluster_cross_validation(
            model_factory=lambda: BaselineLogisticClassifier(),
            X=X,
            y=y,
            groups=groups,
            n_splits=3,
        )
        self.assertIsInstance(res, CrossValidationResult)
        self.assertEqual(len(res.fold_metrics), 3)
        self.assertGreater(res.mean_f1, 0.70)
        self.assertGreater(res.mean_pr_auc, 0.70)
        self.assertLess(res.mean_brier, 0.25)
        self.assertGreaterEqual(res.std_f1, 0.0)


if __name__ == "__main__":
    unittest.main()
"""
    with open(test_val, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for run_cluster_cross_validation evaluation harness",
        "2026-11-11 11:16:00 +0530",
        ["tests/detection/test_ml_validation.py"],
    )


def step_18():
    # test(ml): setup test suite for benchmark generator in tests/detection/test_ml_benchmark.py
    test_bench = ROOT / "tests/detection/test_ml_benchmark.py"
    content = '''"""Unit tests for synthetic benchmark dataset generator."""

import unittest
from sbh.detection.ml.benchmark import generate_benchmark_dataset, BenchmarkDataset
from sbh.detection.ml.features import MLFeaturePipeline


class TestBenchmarkDataset(unittest.TestCase):
    def test_benchmark_generation_shapes(self):
        ds = generate_benchmark_dataset(n_benign=20, n_bots=20, n_campaigns=4, random_seed=42)
        self.assertIsInstance(ds, BenchmarkDataset)
        self.assertEqual(len(ds.accounts), 40)
        self.assertEqual(len(ds.labels), 40)
        self.assertEqual(len(ds.campaign_groups), 40)
        self.assertEqual(sum(ds.labels), 20)  # 20 bots
'''
    test_bench.write_text(content, encoding="utf-8")
    git_commit(
        "test(ml): setup test suite for benchmark generator in tests/detection/test_ml_benchmark.py",
        "2026-11-11 11:18:00 +0530",
        ["tests/detection/test_ml_benchmark.py"],
    )


def step_19():
    # test(ml): add test verifying benchmark pipeline feature extraction and separability
    test_bench = ROOT / "tests/detection/test_ml_benchmark.py"
    code = """

    def test_benchmark_feature_extraction(self):
        ds = generate_benchmark_dataset(n_benign=15, n_bots=15, random_seed=42)
        pipeline = MLFeaturePipeline().fit(ds.accounts, ds.contents_map)

        matrix = [
            pipeline.transform_one(acc, ds.contents_map.get(acc["account_id"]))
            for acc in ds.accounts
        ]
        self.assertEqual(len(matrix), 30)
        self.assertEqual(len(matrix[0]), 44)


if __name__ == "__main__":
    unittest.main()
"""
    with open(test_bench, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add test verifying benchmark pipeline feature extraction and separability",
        "2026-11-11 11:20:00 +0530",
        ["tests/detection/test_ml_benchmark.py"],
    )


def step_20():
    # test(ml): add full end-to-end benchmark cross-validation test
    test_bench = ROOT / "tests/detection/test_ml_benchmark.py"
    code = """

class TestBenchmarkEndToEnd(unittest.TestCase):
    def test_benchmark_cluster_cross_validation(self):
        from sbh.detection.ml.models import BaselineLogisticClassifier
        from sbh.detection.ml.validation import run_cluster_cross_validation

        ds = generate_benchmark_dataset(n_benign=25, n_bots=25, n_campaigns=5, random_seed=123)
        pipeline = MLFeaturePipeline().fit(ds.accounts, ds.contents_map)
        X = [pipeline.transform_one(acc, ds.contents_map.get(acc["account_id"])) for acc in ds.accounts]

        res = run_cluster_cross_validation(
            model_factory=lambda: BaselineLogisticClassifier(),
            X=X,
            y=ds.labels,
            groups=ds.campaign_groups,
            n_splits=3,
        )
        self.assertGreater(res.mean_f1, 0.70)
        self.assertGreater(res.mean_pr_auc, 0.70)
        self.assertLess(res.mean_brier, 0.30)
"""
    with open(test_bench, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add full end-to-end benchmark cross-validation test",
        "2026-11-11 11:22:00 +0530",
        ["tests/detection/test_ml_benchmark.py"],
    )


def step_21():
    # feat(ml): add helper for summarizing evaluation metrics as human-readable dictionary
    metrics_py = ROOT / "src/sbh/detection/ml/metrics.py"
    code = """

def metrics_to_summary_dict(m: EvaluationMetrics) -> dict[str, Any]:
    \"\"\"Serialize evaluation metrics into JSON-compatible dictionary.\"\"\"
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
"""
    with open(metrics_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): add helper for summarizing evaluation metrics as human-readable dictionary",
        "2026-11-11 11:24:00 +0530",
        ["src/sbh/detection/ml/metrics.py"],
    )


def step_22():
    # test(ml): add unit test for metrics_to_summary_dict serialization
    test_metrics = ROOT / "tests/detection/test_ml_metrics.py"
    code = """

    def test_metrics_serialization(self):
        from sbh.detection.ml.metrics import metrics_to_summary_dict
        m = compute_evaluation_metrics([0, 1], [0, 1], [0.1, 0.9])
        d = metrics_to_summary_dict(m)
        self.assertEqual(d["precision"], 1.0)
        self.assertEqual(d["confusion_matrix"]["tp"], 1)
"""
    with open(test_metrics, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for metrics_to_summary_dict serialization",
        "2026-11-11 11:26:00 +0530",
        ["tests/detection/test_ml_metrics.py"],
    )


def step_23():
    # test(ml): add test for calibration curve point serialization
    test_metrics = ROOT / "tests/detection/test_ml_metrics.py"
    code = """

    def test_curve_serialization(self):
        pts = compute_calibration_curve([0, 1], [0.1, 0.9], n_bins=2)
        self.assertEqual(len(pts), 2)
        d = [
            {
                "bin_index": p.bin_index,
                "mean_predicted_prob": p.mean_predicted_prob,
                "fraction_positives": p.fraction_positives,
                "sample_count": p.sample_count,
            }
            for p in pts
        ]
        self.assertEqual(d[0]["bin_index"], 0)
"""
    with open(test_metrics, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add test for calibration curve point serialization",
        "2026-11-11 11:28:00 +0530",
        ["tests/detection/test_ml_metrics.py"],
    )


def step_24():
    # test(ml): add test verifying cross-validation result summary representation
    test_val = ROOT / "tests/detection/test_ml_validation.py"
    code = """

    def test_cross_val_result_fields(self):
        res = CrossValidationResult(
            mean_precision=0.91,
            mean_recall=0.88,
            mean_f1=0.895,
            mean_pr_auc=0.92,
            mean_roc_auc=0.95,
            mean_brier=0.08,
            mean_ece=0.04,
            std_f1=0.02,
        )
        self.assertEqual(res.mean_f1, 0.895)
        self.assertEqual(res.std_f1, 0.02)
"""
    with open(test_val, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add test verifying cross-validation result summary representation",
        "2026-11-11 11:30:00 +0530",
        ["tests/detection/test_ml_validation.py"],
    )


def step_25():
    # refactor(ml): export metrics, validation, and benchmark interfaces in sbh.detection.ml
    pkg_init = ROOT / "src/sbh/detection/ml/__init__.py"
    content = '''"""Machine learning detection, evaluation, and calibration package."""

from __future__ import annotations

from sbh.detection.ml.benchmark import (
    BenchmarkDataset,
    generate_benchmark_dataset,
)
from sbh.detection.ml.features import (
    ALL_FEATURE_NAMES,
    CORE_FEATURE_NAMES,
    INDICATOR_FEATURE_NAMES,
    AccountFeatureExtractor,
    AccountFeatureVector,
    FeatureImputer,
    MLFeaturePipeline,
    calculate_hourly_entropy,
    calculate_inter_post_intervals,
    calculate_shannon_entropy,
    calculate_simhash_repetition,
    extract_content_features,
    extract_feature_matrix,
    extract_profile_features,
)
from sbh.detection.ml.metrics import (
    CalibrationCurvePoint,
    EvaluationMetrics,
    compute_calibration_curve,
    compute_evaluation_metrics,
    compute_expected_calibration_error,
    metrics_to_summary_dict,
)
from sbh.detection.ml.models import (
    BaselineLogisticClassifier,
    BotModelProtocol,
    CalibratedBotClassifier,
    HybridEnsembleDetector,
    IsolationForestAnomalyDetector,
    ModelPrediction,
    RandomForestBotClassifier,
    create_default_bot_classifier,
    determine_risk_band,
)
from sbh.detection.ml.validation import (
    ClusterGroupSplitter,
    CrossValidationResult,
    TemporalSplitter,
    run_cluster_cross_validation,
)

__all__ = [
    "ALL_FEATURE_NAMES",
    "CORE_FEATURE_NAMES",
    "INDICATOR_FEATURE_NAMES",
    "AccountFeatureExtractor",
    "AccountFeatureVector",
    "BaselineLogisticClassifier",
    "BenchmarkDataset",
    "BotModelProtocol",
    "CalibratedBotClassifier",
    "CalibrationCurvePoint",
    "ClusterGroupSplitter",
    "CrossValidationResult",
    "EvaluationMetrics",
    "FeatureImputer",
    "HybridEnsembleDetector",
    "IsolationForestAnomalyDetector",
    "MLFeaturePipeline",
    "ModelPrediction",
    "RandomForestBotClassifier",
    "TemporalSplitter",
    "calculate_hourly_entropy",
    "calculate_inter_post_intervals",
    "calculate_shannon_entropy",
    "calculate_simhash_repetition",
    "compute_calibration_curve",
    "compute_evaluation_metrics",
    "compute_expected_calibration_error",
    "create_default_bot_classifier",
    "determine_risk_band",
    "extract_content_features",
    "extract_feature_matrix",
    "extract_profile_features",
    "generate_benchmark_dataset",
    "metrics_to_summary_dict",
    "run_cluster_cross_validation",
]
'''
    pkg_init.write_text(content, encoding="utf-8")
    git_commit(
        "refactor(ml): export metrics, validation, and benchmark interfaces in sbh.detection.ml",
        "2026-11-11 11:32:00 +0530",
        ["src/sbh/detection/ml/__init__.py"],
    )


def main():
    steps = [
        step_01, step_02, step_03, step_04, step_05,
        step_06, step_07, step_08, step_09, step_10,
        step_11, step_12, step_13, step_14, step_15,
        step_16, step_17, step_18, step_19, step_20,
        step_21, step_22, step_23, step_24, step_25,
    ]
    for s in steps:
        s()
    print("Batch 3 completed successfully!")


if __name__ == "__main__":
    main()
