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
