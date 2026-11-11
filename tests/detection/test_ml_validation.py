"""Unit tests verifying zero data leakage across cross-validation folds and temporal splits."""

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
