"""Unit tests verifying zero data leakage across cross-validation folds and temporal splits."""

import unittest
from datetime import UTC, datetime

import numpy as np

from sbh.detection.ml.models import BaselineLogisticClassifier
from sbh.detection.ml.validation import (
    ClusterGroupSplitter,
    CrossValidationResult,
    TemporalSplitter,
    run_cluster_cross_validation,
)


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


class TestTemporalSplitter(unittest.TestCase):
    def test_chronological_split(self):
        cutoff = datetime(2026, 11, 5, 0, 0, 0, tzinfo=UTC)
        timestamps = [
            datetime(2026, 11, 1, tzinfo=UTC),
            datetime(2026, 11, 3, tzinfo=UTC),
            datetime(2026, 11, 7, tzinfo=UTC),
            datetime(2026, 11, 9, tzinfo=UTC),
        ]
        splitter = TemporalSplitter(cutoff_time=cutoff)
        train_idx, test_idx = splitter.split(timestamps)
        self.assertEqual(train_idx, [0, 1])
        self.assertEqual(test_idx, [2, 3])

    def test_empty_split_raises(self):
        cutoff = datetime(2026, 12, 1, tzinfo=UTC)
        timestamps = [datetime(2026, 11, 1, tzinfo=UTC)]
        splitter = TemporalSplitter(cutoff_time=cutoff)
        with self.assertRaises(ValueError):
            splitter.split(timestamps)


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
