"""Unit tests for synthetic benchmark dataset generator."""

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
