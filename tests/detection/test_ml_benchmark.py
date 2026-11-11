"""Unit tests for synthetic benchmark dataset generator."""

import unittest

from sbh.detection.ml.benchmark import BenchmarkDataset, generate_benchmark_dataset
from sbh.detection.ml.features import MLFeaturePipeline


class TestBenchmarkDataset(unittest.TestCase):
    def test_benchmark_generation_shapes(self):
        ds = generate_benchmark_dataset(n_benign=20, n_bots=20, n_campaigns=4, random_seed=42)
        self.assertIsInstance(ds, BenchmarkDataset)
        self.assertEqual(len(ds.accounts), 40)
        self.assertEqual(len(ds.labels), 40)
        self.assertEqual(len(ds.campaign_groups), 40)
        self.assertEqual(sum(ds.labels), 20)  # 20 bots


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


class TestBenchmarkEndToEnd(unittest.TestCase):
    def test_benchmark_cluster_cross_validation(self):
        from sbh.detection.ml.models import BaselineLogisticClassifier
        from sbh.detection.ml.validation import run_cluster_cross_validation

        ds = generate_benchmark_dataset(n_benign=50, n_bots=50, n_campaigns=8, random_seed=42)
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
