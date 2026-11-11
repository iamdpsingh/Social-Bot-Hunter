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
