"""Unit tests for ML bot classification models, calibration, and anomaly detection."""

import unittest
import numpy as np
from sbh.detection.ml.models import (
    determine_risk_band,
    BaselineLogisticClassifier,
    RandomForestBotClassifier,
    CalibratedBotClassifier,
    IsolationForestAnomalyDetector,
    HybridEnsembleDetector,
    create_default_bot_classifier,
    ModelPrediction,
)
from sbh.detection.ml.features import ALL_FEATURE_NAMES


def make_synthetic_dataset(n_samples: int = 100, n_features: int = 44, random_state: int = 42):
    rng = np.random.RandomState(random_state)
    half = n_samples // 2
    # Benign: lower activity, higher entropy, higher followers
    X_benign = rng.normal(loc=0.0, scale=1.0, size=(half, n_features))
    y_benign = np.zeros(half, dtype=np.int32)

    # Bot: higher post repetition, lower entropy, young account
    X_bot = rng.normal(loc=2.0, scale=1.0, size=(half, n_features))
    y_bot = np.ones(half, dtype=np.int32)

    X = np.vstack([X_benign, X_bot])
    y = np.concatenate([y_benign, y_bot])
    indices = rng.permutation(n_samples)
    return X[indices], y[indices]


class TestDetermineRiskBand(unittest.TestCase):
    def test_risk_bands(self):
        self.assertEqual(determine_risk_band(0.10), "low")
        self.assertEqual(determine_risk_band(0.45), "medium")
        self.assertEqual(determine_risk_band(0.65), "high")
        self.assertEqual(determine_risk_band(0.85), "critical")


class TestBaselineLogisticClassifier(unittest.TestCase):
    def test_fit_and_predict(self):
        X, y = make_synthetic_dataset(n_samples=80)
        clf = BaselineLogisticClassifier().fit(X, y)
        self.assertTrue(clf.is_fitted)

        probs = clf.predict_proba(X)
        self.assertEqual(len(probs), 80)
        for p in probs:
            self.assertGreaterEqual(p, 0.0)
            self.assertLessEqual(p, 1.0)

        preds = clf.predict(X)
        self.assertEqual(len(preds), 80)
        accuracy = np.mean(np.array(preds) == y)
        self.assertGreater(accuracy, 0.80)


    def test_coefficients_mapping(self):
        X, y = make_synthetic_dataset(n_samples=60, n_features=44)
        clf = BaselineLogisticClassifier().fit(X, y)
        coefs = clf.get_coefficients(ALL_FEATURE_NAMES)
        self.assertEqual(len(coefs), 44)
        self.assertIn("account_age_days", coefs)
        self.assertIn("is_missing_account_age_days", coefs)


class TestRandomForestBotClassifier(unittest.TestCase):
    def test_rf_training_and_oob(self):
        X, y = make_synthetic_dataset(n_samples=100)
        rf = RandomForestBotClassifier(n_estimators=30, max_depth=5).fit(X, y)
        self.assertTrue(rf.is_fitted)

        probs = rf.predict_proba(X)
        self.assertEqual(len(probs), 100)
        for p in probs:
            self.assertGreaterEqual(p, 0.0)
            self.assertLessEqual(p, 1.0)

        preds = rf.predict(X)
        accuracy = np.mean(np.array(preds) == y)
        self.assertGreater(accuracy, 0.85)


    def test_feature_importances(self):
        X, y = make_synthetic_dataset(n_samples=80, n_features=44)
        rf = RandomForestBotClassifier(n_estimators=30).fit(X, y)
        imps = rf.get_feature_importances(ALL_FEATURE_NAMES)
        self.assertEqual(len(imps), 44)
        total_imp = sum(imps.values())
        self.assertAlmostEqual(total_imp, 1.0, places=1)


class TestCalibratedBotClassifier(unittest.TestCase):
    def test_calibrated_probabilities(self):
        X, y = make_synthetic_dataset(n_samples=120)
        cal = CalibratedBotClassifier(cv=3).fit(X, y)
        self.assertTrue(cal.is_fitted)

        probs = cal.predict_proba(X)
        self.assertEqual(len(probs), 120)
        for p in probs:
            self.assertGreaterEqual(p, 0.0)
            self.assertLessEqual(p, 1.0)

        preds = cal.predict(X)
        accuracy = np.mean(np.array(preds) == y)
        self.assertGreater(accuracy, 0.85)
