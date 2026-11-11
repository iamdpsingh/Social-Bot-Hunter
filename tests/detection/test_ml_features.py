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


class TestInterPostIntervals(unittest.TestCase):
    def test_insufficient_timestamps(self):
        m, s = calculate_inter_post_intervals([])
        self.assertIsNone(m)
        self.assertIsNone(s)
        m, s = calculate_inter_post_intervals([datetime.now(timezone.utc)])
        self.assertIsNone(m)

    def test_exact_periodic_intervals(self):
        # Exactly 60 seconds apart: mean=60.0, std=0.0
        ts = [
            datetime(2026, 11, 10, 10, 0, 0, tzinfo=timezone.utc),
            datetime(2026, 11, 10, 10, 1, 0, tzinfo=timezone.utc),
            datetime(2026, 11, 10, 10, 2, 0, tzinfo=timezone.utc),
        ]
        mean_sec, std_sec = calculate_inter_post_intervals(ts)
        self.assertEqual(mean_sec, 60.0)
        self.assertEqual(std_sec, 0.0)


class TestSimHashRepetition(unittest.TestCase):
    def test_empty_or_single_text(self):
        self.assertEqual(calculate_simhash_repetition([]), (0, 0.0))
        self.assertEqual(calculate_simhash_repetition(["hello"]), (1, 0.0))

    def test_duplicate_spam_clusters(self):
        texts = [
            "BREAKING NEWS: Check out this amazing free coin drop now!",
            "BREAKING NEWS: Check out this amazing free coin drop now!",
            "BREAKING NEWS: Check out this amazing free coin drop now!",
            "Completely distinct organic comment about the weather today.",
        ]
        max_c, dup_r = calculate_simhash_repetition(texts)
        self.assertEqual(max_c, 3)
        self.assertEqual(dup_r, 0.5)  # 2 duplicates out of 4 total


class TestProfileFeatures(unittest.TestCase):
    def test_complete_profile(self):
        ref = datetime(2026, 11, 10, 12, 0, 0, tzinfo=timezone.utc)
        acc = {
            "account_id": "user_101",
            "username": "crypto_bot_7788",
            "created_at": datetime(2026, 11, 8, 12, 0, 0, tzinfo=timezone.utc),
            "followers_count": 50,
            "following_count": 1000,
            "default_profile_image": True,
            "description": "Follow me for crypto gems! https://spam.xyz",
            "statuses_count": 500,
        }
        feats = extract_profile_features(acc, ref)
        self.assertEqual(feats["account_age_days"], 2.0)
        self.assertEqual(feats["followers_count"], 50.0)
        self.assertEqual(feats["following_count"], 1000.0)
        self.assertEqual(feats["follower_following_ratio"], 0.05)
        self.assertEqual(feats["has_default_profile_image"], 1.0)
        self.assertEqual(feats["description_has_url"], 1.0)
        self.assertEqual(feats["screen_name_digits"], 4.0)


class TestContentFeatures(unittest.TestCase):
    def test_content_ratios(self):
        contents = [
            {"text": "Check out https://example.com/deal", "created_at": "2026-11-10T10:00:00Z"},
            {"text": "Hey @friend look at this!", "created_at": "2026-11-10T11:00:00Z"},
            {"text": "Just another normal post", "created_at": "2026-11-10T12:00:00Z"},
            {"text": "Dual link https://link.org with @someone", "created_at": "2026-11-10T13:00:00Z"},
        ]
        feats = extract_content_features(contents, account_age_days=1.0)
        self.assertEqual(feats["url_post_ratio"], 0.5)
        self.assertEqual(feats["mention_post_ratio"], 0.5)
        self.assertEqual(feats["simhash_max_cluster_size"], 1.0)
        self.assertEqual(feats["simhash_duplicate_ratio"], 0.0)


class TestAccountFeatureExtractor(unittest.TestCase):
    def test_extract_all_core_features_present(self):
        extractor = AccountFeatureExtractor()
        acc = {
            "account_id": "acc_001",
            "username": "bot_99",
            "created_at": datetime(2026, 11, 1, tzinfo=timezone.utc),
            "followers_count": 10,
            "following_count": 100,
            "default_profile_image": False,
            "description": "Just an account",
            "statuses_count": 5,
        }
        contents = [{"text": "Hello world", "created_at": datetime(2026, 11, 5, tzinfo=timezone.utc)}]
        vec = extractor.extract(acc, contents)
        self.assertEqual(vec.account_id, "acc_001")
        for name in CORE_FEATURE_NAMES:
            self.assertIn(name, vec.features)


    def test_minimal_profile_missing_fields(self):
        extractor = AccountFeatureExtractor()
        acc = {"account_id": "bare_acc"}
        vec = extractor.extract(acc, [])
        self.assertEqual(vec.account_id, "bare_acc")
        self.assertIsNone(vec.features["followers_count"])
        self.assertIsNone(vec.features["account_age_days"])
        self.assertIsNone(vec.features["hourly_entropy"])
