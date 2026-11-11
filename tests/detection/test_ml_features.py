"""Unit tests for ML feature extraction, imputation, and vectorization."""

import unittest
from datetime import datetime, timezone
from sbh.detection.ml.features import (
    calculate_shannon_entropy,
    calculate_hourly_entropy,
    calculate_inter_post_intervals,
    calculate_simhash_repetition,
    extract_profile_features,
    extract_content_features,
    AccountFeatureExtractor,
    FeatureImputer,
    MLFeaturePipeline,
    extract_feature_matrix,
    CORE_FEATURE_NAMES,
    ALL_FEATURE_NAMES,
)


class TestShannonEntropy(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(calculate_shannon_entropy(""), 0.0)

    def test_single_repeated_char(self):
        self.assertEqual(calculate_shannon_entropy("aaaaaaa"), 0.0)

    def test_random_string_positive_entropy(self):
        h = calculate_shannon_entropy("bot_hunter_9988_xyz")
        self.assertGreater(h, 3.0)


class TestHourlyEntropy(unittest.TestCase):
    def test_empty_timestamps(self):
        self.assertEqual(calculate_hourly_entropy([]), 0.0)

    def test_single_hour_spam(self):
        # 10 posts all at hour 3
        ts = [datetime(2026, 11, 10, 3, i, 0, tzinfo=timezone.utc) for i in range(10)]
        self.assertEqual(calculate_hourly_entropy(ts), 0.0)

    def test_uniform_circadian_entropy(self):
        # 24 posts evenly spaced across 24 hours
        ts = [datetime(2026, 11, 10, h, 0, 0, tzinfo=timezone.utc) for h in range(24)]
        self.assertAlmostEqual(calculate_hourly_entropy(ts), 1.0, places=2)
