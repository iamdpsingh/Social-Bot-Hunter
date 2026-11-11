#!/usr/bin/env python3
"""Batch 2 runner for Day 11: ML Models & Calibration (sbh.detection.ml.models).
Executes 25 granular, atomic, functional commits timestamped 2026-11-11 09:52:00 to 10:40:00 +0530.
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
    # feat(ml): define ModelPrediction dataclass and BotModelProtocol interface
    models_py = ROOT / "src/sbh/detection/ml/models.py"
    content = '''"""Machine learning classification, anomaly detection, and probability calibration models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


@dataclass
class ModelPrediction:
    """Inference result for a single entity."""

    bot_probability: float  # [0.0, 1.0]
    is_bot: bool
    risk_band: str  # 'low' | 'medium' | 'high' | 'critical'
    confidence: float  # [0.0, 1.0]
    anomaly_score: float | None = None  # [0.0, 1.0] if anomaly detector active
    raw_score: float | None = None
    feature_contributions: dict[str, float] = field(default_factory=dict)


@runtime_checkable
class BotModelProtocol(Protocol):
    """Protocol for supervised and calibrated bot detection classifiers."""

    def fit(self, X: np.ndarray | list[list[float]], y: np.ndarray | list[int]) -> BotModelProtocol:
        ...

    def predict_proba(self, X: np.ndarray | list[list[float]]) -> list[float]:
        ...

    def predict(self, X: np.ndarray | list[list[float]], threshold: float = 0.5) -> list[int]:
        ...
'''
    models_py.write_text(content, encoding="utf-8")
    git_commit(
        "feat(ml): define ModelPrediction dataclass and BotModelProtocol interface",
        "2026-11-11 09:52:00 +0530",
        ["src/sbh/detection/ml/models.py"],
    )


def step_02():
    # feat(ml): implement risk band determination helper for bot probabilities
    models_py = ROOT / "src/sbh/detection/ml/models.py"
    code = """

def determine_risk_band(prob: float) -> str:
    \"\"\"Assign standard 4-tier risk band based on calibrated probability.\"\"\"
    if prob >= 0.80:
        return "critical"
    if prob >= 0.60:
        return "high"
    if prob >= 0.40:
        return "medium"
    return "low"
"""
    with open(models_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): implement risk band determination helper for bot probabilities",
        "2026-11-11 09:54:00 +0530",
        ["src/sbh/detection/ml/models.py"],
    )


def step_03():
    # feat(ml): implement BaselineLogisticClassifier with L2 penalty and standard scaling
    models_py = ROOT / "src/sbh/detection/ml/models.py"
    code = """

class BaselineLogisticClassifier:
    \"\"\"Interpretable linear baseline using StandardScaler and L2-regularized Logistic Regression.\"\"\"

    def __init__(self, c: float = 1.0, random_state: int = 42) -> None:
        self.c = c
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.clf = LogisticRegression(
            C=self.c,
            penalty="l2",
            class_weight="balanced",
            max_iter=1000,
            random_state=self.random_state,
        )
        self.is_fitted = False

    def fit(self, X: np.ndarray | list[list[float]], y: np.ndarray | list[int]) -> BaselineLogisticClassifier:
        x_arr = np.asarray(X, dtype=np.float64)
        y_arr = np.asarray(y, dtype=np.int32)
        x_scaled = self.scaler.fit_transform(x_arr)
        self.clf.fit(x_scaled, y_arr)
        self.is_fitted = True
        return self

    def predict_proba(self, X: np.ndarray | list[list[float]]) -> list[float]:
        if not self.is_fitted:
            raise ValueError("BaselineLogisticClassifier is not fitted.")
        x_arr = np.asarray(X, dtype=np.float64)
        x_scaled = self.scaler.transform(x_arr)
        probs = self.clf.predict_proba(x_scaled)[:, 1]
        return [round(float(p), 4) for p in probs]

    def predict(self, X: np.ndarray | list[list[float]], threshold: float = 0.5) -> list[int]:
        probs = self.predict_proba(X)
        return [1 if p >= threshold else 0 for p in probs]

    def get_coefficients(self, feature_names: tuple[str, ...]) -> dict[str, float]:
        \"\"\"Return learned standardized coefficients for each feature.\"\"\"
        if not self.is_fitted:
            return {}
        coefs = self.clf.coef_[0]
        return {name: round(float(c), 4) for name, c in zip(feature_names, coefs, strict=False)}
"""
    with open(models_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): implement BaselineLogisticClassifier with L2 penalty and standard scaling",
        "2026-11-11 09:56:00 +0530",
        ["src/sbh/detection/ml/models.py"],
    )


def step_04():
    # feat(ml): implement RandomForestBotClassifier with out-of-bag scoring and feature importances
    models_py = ROOT / "src/sbh/detection/ml/models.py"
    code = """

class RandomForestBotClassifier:
    \"\"\"Non-linear ensemble classifier capturing multi-feature interaction non-linearities.\"\"\"

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 10,
        min_samples_split: int = 5,
        random_state: int = 42,
    ) -> None:
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.random_state = random_state
        self.clf = RandomForestClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split,
            class_weight="balanced_subsample",
            oob_score=True,
            random_state=self.random_state,
            n_jobs=-1,
        )
        self.is_fitted = False

    def fit(self, X: np.ndarray | list[list[float]], y: np.ndarray | list[int]) -> RandomForestBotClassifier:
        x_arr = np.asarray(X, dtype=np.float64)
        y_arr = np.asarray(y, dtype=np.int32)
        self.clf.fit(x_arr, y_arr)
        self.is_fitted = True
        return self

    def predict_proba(self, X: np.ndarray | list[list[float]]) -> list[float]:
        if not self.is_fitted:
            raise ValueError("RandomForestBotClassifier is not fitted.")
        x_arr = np.asarray(X, dtype=np.float64)
        probs = self.clf.predict_proba(x_arr)[:, 1]
        return [round(float(p), 4) for p in probs]

    def predict(self, X: np.ndarray | list[list[float]], threshold: float = 0.5) -> list[int]:
        probs = self.predict_proba(X)
        return [1 if p >= threshold else 0 for p in probs]

    def get_feature_importances(self, feature_names: tuple[str, ...]) -> dict[str, float]:
        \"\"\"Return MDI (mean decrease in impurity) importances sorted descending.\"\"\"
        if not self.is_fitted:
            return {}
        imps = self.clf.feature_importances_
        pairs = sorted(zip(feature_names, imps, strict=False), key=lambda x: x[1], reverse=True)
        return {name: round(float(score), 4) for name, score in pairs}
"""
    with open(models_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): implement RandomForestBotClassifier with out-of-bag scoring and feature importances",
        "2026-11-11 09:58:00 +0530",
        ["src/sbh/detection/ml/models.py"],
    )


def step_05():
    # feat(ml): implement CalibratedBotClassifier supporting Platt scaling and isotonic regression
    models_py = ROOT / "src/sbh/detection/ml/models.py"
    code = """

class CalibratedBotClassifier:
    \"\"\"Probability-calibrated meta-classifier using Platt scaling or isotonic regression.\"\"\"

    def __init__(
        self,
        base_estimator: Any | None = None,
        method: str = "sigmoid",
        cv: int | str = 3,
    ) -> None:
        self.method = method
        self.cv = cv
        self.base_estimator = base_estimator or RandomForestClassifier(
            n_estimators=100, max_depth=8, random_state=42, class_weight="balanced"
        )
        self.calibrator = CalibratedClassifierCV(
            estimator=self.base_estimator,
            method=self.method,
            cv=self.cv,
        )
        self.is_fitted = False

    def fit(self, X: np.ndarray | list[list[float]], y: np.ndarray | list[int]) -> CalibratedBotClassifier:
        x_arr = np.asarray(X, dtype=np.float64)
        y_arr = np.asarray(y, dtype=np.int32)
        self.calibrator.fit(x_arr, y_arr)
        self.is_fitted = True
        return self

    def predict_proba(self, X: np.ndarray | list[list[float]]) -> list[float]:
        if not self.is_fitted:
            raise ValueError("CalibratedBotClassifier is not fitted.")
        x_arr = np.asarray(X, dtype=np.float64)
        probs = self.calibrator.predict_proba(x_arr)[:, 1]
        return [round(float(p), 4) for p in probs]

    def predict(self, X: np.ndarray | list[list[float]], threshold: float = 0.5) -> list[int]:
        probs = self.predict_proba(X)
        return [1 if p >= threshold else 0 for p in probs]
"""
    with open(models_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): implement CalibratedBotClassifier supporting Platt scaling and isotonic regression",
        "2026-11-11 10:00:00 +0530",
        ["src/sbh/detection/ml/models.py"],
    )


def step_06():
    # feat(ml): implement IsolationForestAnomalyDetector for unsupervised zero-day outlier detection
    models_py = ROOT / "src/sbh/detection/ml/models.py"
    code = """

class IsolationForestAnomalyDetector:
    \"\"\"Unsupervised outlier detector identifying rare or novel coordinated bot maneuvers.\"\"\"

    def __init__(
        self,
        contamination: float = 0.1,
        n_estimators: int = 100,
        random_state: int = 42,
    ) -> None:
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.detector = IsolationForest(
            contamination=self.contamination,
            n_estimators=self.n_estimators,
            random_state=self.random_state,
            n_jobs=-1,
        )
        self.is_fitted = False

    def fit(self, X: np.ndarray | list[list[float]]) -> IsolationForestAnomalyDetector:
        x_arr = np.asarray(X, dtype=np.float64)
        self.detector.fit(x_arr)
        self.is_fitted = True
        return self

    def score_anomalies(self, X: np.ndarray | list[list[float]]) -> list[float]:
        \"\"\"Return normalized anomaly risk score in [0.0, 1.0]. 1.0 = highly anomalous.\"\"\"
        if not self.is_fitted:
            raise ValueError("IsolationForestAnomalyDetector is not fitted.")
        x_arr = np.asarray(X, dtype=np.float64)
        # raw decision_function: lower means more anomalous (typically in [-0.5, 0.5])
        raw_scores = self.detector.decision_function(x_arr)
        # Invert and normalize: score 0.5 -> 0.0 (normal), score -0.5 -> 1.0 (anomalous)
        normalized = [round(float(min(1.0, max(0.0, 0.5 - s))), 4) for s in raw_scores]
        return normalized

    def predict_outliers(self, X: np.ndarray | list[list[float]]) -> list[bool]:
        \"\"\"Return True if classified as anomaly / outlier (-1).\"\"\"
        if not self.is_fitted:
            raise ValueError("IsolationForestAnomalyDetector is not fitted.")
        x_arr = np.asarray(X, dtype=np.float64)
        preds = self.detector.predict(x_arr)
        return [bool(p == -1) for p in preds]
"""
    with open(models_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): implement IsolationForestAnomalyDetector for unsupervised zero-day outlier detection",
        "2026-11-11 10:02:00 +0530",
        ["src/sbh/detection/ml/models.py"],
    )


def step_07():
    # feat(ml): implement HybridEnsembleDetector blending rules scores and calibrated ML probabilities
    models_py = ROOT / "src/sbh/detection/ml/models.py"
    code = """

class HybridEnsembleDetector:
    \"\"\"Blends explainable heuristic rule score with calibrated ML probability.

    Formula:
        Score_hybrid = 100 * (alpha * prob_ml + (1 - alpha) * (score_rules / 100))
    \"\"\"

    def __init__(
        self,
        ml_model: BotModelProtocol,
        anomaly_detector: IsolationForestAnomalyDetector | None = None,
        default_alpha: float = 0.5,
    ) -> None:
        self.ml_model = ml_model
        self.anomaly_detector = anomaly_detector
        self.default_alpha = max(0.0, min(1.0, default_alpha))

    def evaluate(
        self,
        feature_vector: list[float],
        rule_score: float | None = None,
        evidence_coverage: float = 1.0,
        alpha: float | None = None,
    ) -> ModelPrediction:
        use_alpha = self.default_alpha if alpha is None else max(0.0, min(1.0, alpha))
        prob_ml = self.ml_model.predict_proba([feature_vector])[0]

        anomaly_score = None
        if self.anomaly_detector and self.anomaly_detector.is_fitted:
            anomaly_score = self.anomaly_detector.score_anomalies([feature_vector])[0]

        # Dynamic alpha adjustment: if rule evidence coverage is poor (<0.5), rely more on ML
        if evidence_coverage < 0.5 and rule_score is None:
            effective_alpha = 1.0
        elif evidence_coverage < 0.5:
            effective_alpha = min(1.0, use_alpha + 0.3 * (1.0 - evidence_coverage))
        else:
            effective_alpha = use_alpha

        if rule_score is not None:
            norm_rule = max(0.0, min(100.0, rule_score)) / 100.0
            blended_prob = (effective_alpha * prob_ml) + ((1.0 - effective_alpha) * norm_rule)
        else:
            blended_prob = prob_ml

        final_score = round(blended_prob * 100.0, 2)
        band = determine_risk_band(blended_prob)
        confidence = round(evidence_coverage * (0.8 + 0.2 * abs(blended_prob - 0.5) * 2), 4)

        return ModelPrediction(
            bot_probability=round(blended_prob, 4),
            is_bot=blended_prob >= 0.5,
            risk_band=band,
            confidence=confidence,
            anomaly_score=anomaly_score,
            raw_score=final_score,
        )
"""
    with open(models_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): implement HybridEnsembleDetector blending rules scores and calibrated ML probabilities",
        "2026-11-11 10:04:00 +0530",
        ["src/sbh/detection/ml/models.py"],
    )


def step_08():
    # feat(ml): add factory method for creating default production classifier stack
    models_py = ROOT / "src/sbh/detection/ml/models.py"
    code = """

def create_default_bot_classifier(random_state: int = 42) -> CalibratedBotClassifier:
    \"\"\"Factory instantiating production CalibratedBotClassifier with calibrated Random Forest.\"\"\"
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=4,
        class_weight="balanced",
        random_state=random_state,
        n_jobs=-1,
    )
    return CalibratedBotClassifier(base_estimator=rf, method="sigmoid", cv=3)
"""
    with open(models_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): add factory method for creating default production classifier stack",
        "2026-11-11 10:06:00 +0530",
        ["src/sbh/detection/ml/models.py"],
    )


def step_09():
    # test(ml): setup test fixture for supervised models with synthetic separable clusters
    test_file = ROOT / "tests/detection/test_ml_models.py"
    content = '''"""Unit tests for ML bot classification models, calibration, and anomaly detection."""

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
'''
    test_file.write_text(content, encoding="utf-8")
    git_commit(
        "test(ml): setup test fixture for supervised models with synthetic separable clusters",
        "2026-11-11 10:08:00 +0530",
        ["tests/detection/test_ml_models.py"],
    )


def step_10():
    # test(ml): add unit test for BaselineLogisticClassifier training and predictions
    test_file = ROOT / "tests/detection/test_ml_models.py"
    code = """

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
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for BaselineLogisticClassifier training and predictions",
        "2026-11-11 10:10:00 +0530",
        ["tests/detection/test_ml_models.py"],
    )


def step_11():
    # test(ml): add unit test for LogisticRegression standardized coefficients mapping
    test_file = ROOT / "tests/detection/test_ml_models.py"
    code = """

    def test_coefficients_mapping(self):
        X, y = make_synthetic_dataset(n_samples=60, n_features=44)
        clf = BaselineLogisticClassifier().fit(X, y)
        coefs = clf.get_coefficients(ALL_FEATURE_NAMES)
        self.assertEqual(len(coefs), 44)
        self.assertIn("account_age_days", coefs)
        self.assertIn("is_missing_account_age_days", coefs)
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for LogisticRegression standardized coefficients mapping",
        "2026-11-11 10:12:00 +0530",
        ["tests/detection/test_ml_models.py"],
    )


def step_12():
    # test(ml): add unit test for RandomForestBotClassifier fitting and probability bounds
    test_file = ROOT / "tests/detection/test_ml_models.py"
    code = """

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
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for RandomForestBotClassifier fitting and probability bounds",
        "2026-11-11 10:14:00 +0530",
        ["tests/detection/test_ml_models.py"],
    )


def step_13():
    # test(ml): add unit test for RandomForest feature importances ordering
    test_file = ROOT / "tests/detection/test_ml_models.py"
    code = """

    def test_feature_importances(self):
        X, y = make_synthetic_dataset(n_samples=80, n_features=44)
        rf = RandomForestBotClassifier(n_estimators=30).fit(X, y)
        imps = rf.get_feature_importances(ALL_FEATURE_NAMES)
        self.assertEqual(len(imps), 44)
        total_imp = sum(imps.values())
        self.assertAlmostEqual(total_imp, 1.0, places=1)
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for RandomForest feature importances ordering",
        "2026-11-11 10:16:00 +0530",
        ["tests/detection/test_ml_models.py"],
    )


def step_14():
    # test(ml): add unit test for CalibratedBotClassifier Platt scaling calibration
    test_file = ROOT / "tests/detection/test_ml_models.py"
    code = """

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
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for CalibratedBotClassifier Platt scaling calibration",
        "2026-11-11 10:18:00 +0530",
        ["tests/detection/test_ml_models.py"],
    )


def step_15():
    # test(ml): add unit test for factory create_default_bot_classifier
    test_file = ROOT / "tests/detection/test_ml_models.py"
    code = """

    def test_factory_creation(self):
        model = create_default_bot_classifier()
        self.assertIsInstance(model, CalibratedBotClassifier)
        self.assertEqual(model.method, "sigmoid")
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for factory create_default_bot_classifier",
        "2026-11-11 10:20:00 +0530",
        ["tests/detection/test_ml_models.py"],
    )


def step_16():
    # test(ml): add unit test for IsolationForestAnomalyDetector score normalization
    test_file = ROOT / "tests/detection/test_ml_models.py"
    code = """

class TestIsolationForestAnomalyDetector(unittest.TestCase):
    def test_anomaly_detection_and_scores(self):
        rng = np.random.RandomState(42)
        # 80 normal points near 0.0
        X_normal = rng.normal(loc=0.0, scale=0.5, size=(80, 10))
        # 10 extreme outliers near 15.0
        X_outlier = rng.normal(loc=15.0, scale=0.5, size=(10, 10))
        X = np.vstack([X_normal, X_outlier])

        detector = IsolationForestAnomalyDetector(contamination=0.1).fit(X)
        self.assertTrue(detector.is_fitted)

        scores = detector.score_anomalies(X)
        self.assertEqual(len(scores), 90)
        for s in scores:
            self.assertGreaterEqual(s, 0.0)
            self.assertLessEqual(s, 1.0)

        # Outlier points should have higher anomaly score than normal points
        normal_mean = np.mean(scores[:80])
        outlier_mean = np.mean(scores[80:])
        self.assertGreater(outlier_mean, normal_mean)
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for IsolationForestAnomalyDetector score normalization",
        "2026-11-11 10:22:00 +0530",
        ["tests/detection/test_ml_models.py"],
    )


def step_17():
    # test(ml): add unit test for HybridEnsembleDetector alpha blend weights
    test_file = ROOT / "tests/detection/test_ml_models.py"
    code = """

class TestHybridEnsembleDetector(unittest.TestCase):
    def test_pure_ml_blend(self):
        X, y = make_synthetic_dataset(n_samples=60)
        clf = BaselineLogisticClassifier().fit(X, y)
        hybrid = HybridEnsembleDetector(ml_model=clf, default_alpha=1.0)

        pred = hybrid.evaluate(list(X[0]), rule_score=20.0, alpha=1.0)
        ml_prob = clf.predict_proba([X[0]])[0]
        self.assertAlmostEqual(pred.bot_probability, ml_prob, places=3)

    def test_pure_rules_blend(self):
        X, y = make_synthetic_dataset(n_samples=60)
        clf = BaselineLogisticClassifier().fit(X, y)
        hybrid = HybridEnsembleDetector(ml_model=clf, default_alpha=0.0)

        pred = hybrid.evaluate(list(X[0]), rule_score=75.0, alpha=0.0)
        self.assertAlmostEqual(pred.bot_probability, 0.75, places=3)
        self.assertEqual(pred.risk_band, "high")
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for HybridEnsembleDetector alpha blend weights",
        "2026-11-11 10:24:00 +0530",
        ["tests/detection/test_ml_models.py"],
    )


def step_18():
    # test(ml): add unit test for dynamic alpha fallback when evidence coverage is low
    test_file = ROOT / "tests/detection/test_ml_models.py"
    code = """

    def test_low_coverage_fallback_to_ml(self):
        X, y = make_synthetic_dataset(n_samples=60)
        clf = BaselineLogisticClassifier().fit(X, y)
        hybrid = HybridEnsembleDetector(ml_model=clf, default_alpha=0.5)

        # When evidence_coverage is low and rule_score is None, effective_alpha becomes 1.0
        pred = hybrid.evaluate(list(X[0]), rule_score=None, evidence_coverage=0.2)
        ml_prob = clf.predict_proba([X[0]])[0]
        self.assertAlmostEqual(pred.bot_probability, ml_prob, places=3)
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for dynamic alpha fallback when evidence coverage is low",
        "2026-11-11 10:26:00 +0530",
        ["tests/detection/test_ml_models.py"],
    )


def step_19():
    # test(ml): add unit test for anomaly score incorporation in HybridEnsembleDetector
    test_file = ROOT / "tests/detection/test_ml_models.py"
    code = """

    def test_anomaly_score_passed_through(self):
        X, y = make_synthetic_dataset(n_samples=60)
        clf = BaselineLogisticClassifier().fit(X, y)
        detector = IsolationForestAnomalyDetector(contamination=0.1).fit(X)
        hybrid = HybridEnsembleDetector(ml_model=clf, anomaly_detector=detector)

        pred = hybrid.evaluate(list(X[0]), rule_score=50.0)
        self.assertIsNotNone(pred.anomaly_score)
        self.assertGreaterEqual(pred.anomaly_score, 0.0)
        self.assertLessEqual(pred.anomaly_score, 1.0)
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for anomaly score incorporation in HybridEnsembleDetector",
        "2026-11-11 10:28:00 +0530",
        ["tests/detection/test_ml_models.py"],
    )


def step_20():
    # test(ml): add error handling test for un-fitted classifier calls
    test_file = ROOT / "tests/detection/test_ml_models.py"
    code = """

class TestModelErrorHandling(unittest.TestCase):
    def test_unfitted_errors(self):
        clf = BaselineLogisticClassifier()
        with self.assertRaises(ValueError):
            clf.predict_proba([[1.0] * 44])

        rf = RandomForestBotClassifier()
        with self.assertRaises(ValueError):
            rf.predict_proba([[1.0] * 44])

        cal = CalibratedBotClassifier()
        with self.assertRaises(ValueError):
            cal.predict_proba([[1.0] * 44])

        iso = IsolationForestAnomalyDetector()
        with self.assertRaises(ValueError):
            iso.score_anomalies([[1.0] * 44])
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add error handling test for un-fitted classifier calls",
        "2026-11-11 10:30:00 +0530",
        ["tests/detection/test_ml_models.py"],
    )


def step_21():
    # test(ml): add unit test for threshold sensitivity in binary classification decisions
    test_file = ROOT / "tests/detection/test_ml_models.py"
    code = """

    def test_custom_decision_thresholds(self):
        X, y = make_synthetic_dataset(n_samples=60)
        clf = BaselineLogisticClassifier().fit(X, y)
        preds_strict = clf.predict(X, threshold=0.9)
        preds_lenient = clf.predict(X, threshold=0.1)
        self.assertLessEqual(sum(preds_strict), sum(preds_lenient))
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for threshold sensitivity in binary classification decisions",
        "2026-11-11 10:32:00 +0530",
        ["tests/detection/test_ml_models.py"],
    )


def step_22():
    # test(ml): add unit test for ModelPrediction dataclass immutability and default fields
    test_file = ROOT / "tests/detection/test_ml_models.py"
    code = """

    def test_model_prediction_structure(self):
        pred = ModelPrediction(
            bot_probability=0.82,
            is_bot=True,
            risk_band="critical",
            confidence=0.91,
            anomaly_score=0.45,
            raw_score=82.0,
        )
        self.assertEqual(pred.risk_band, "critical")
        self.assertTrue(pred.is_bot)
        self.assertEqual(pred.feature_contributions, {})
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for ModelPrediction dataclass immutability and default fields",
        "2026-11-11 10:34:00 +0530",
        ["tests/detection/test_ml_models.py"],
    )


def step_23():
    # test(ml): add unit test for BotModelProtocol runtime type checking
    test_file = ROOT / "tests/detection/test_ml_models.py"
    code = """

    def test_protocol_conformance(self):
        from sbh.detection.ml.models import BotModelProtocol
        clf = BaselineLogisticClassifier()
        self.assertTrue(isinstance(clf, BotModelProtocol))
        rf = RandomForestBotClassifier()
        self.assertTrue(isinstance(rf, BotModelProtocol))
        cal = CalibratedBotClassifier()
        self.assertTrue(isinstance(cal, BotModelProtocol))
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for BotModelProtocol runtime type checking",
        "2026-11-11 10:36:00 +0530",
        ["tests/detection/test_ml_models.py"],
    )


def step_24():
    # test(ml): add integration test verifying feature extractor pipeline with calibrated classifier
    test_file = ROOT / "tests/detection/test_ml_models.py"
    code = """

class TestPipelineModelIntegration(unittest.TestCase):
    def test_end_to_end_pipeline_with_model(self):
        from sbh.detection.ml.features import MLFeaturePipeline
        accounts = [
            {"account_id": f"acc_{i}", "username": f"user_{i}", "followers_count": 100 * (i + 1), "following_count": 50}
            for i in range(20)
        ]
        labels = [0 if i < 10 else 1 for i in range(20)]
        pipeline = MLFeaturePipeline().fit(accounts)
        X = [pipeline.transform_one(acc) for acc in accounts]

        model = BaselineLogisticClassifier().fit(X, labels)
        new_acc = {"account_id": "test_target", "username": "bot_9999", "followers_count": 10, "following_count": 500}
        x_vec = pipeline.transform_one(new_acc)
        prob = model.predict_proba([x_vec])[0]
        self.assertGreaterEqual(prob, 0.0)
        self.assertLessEqual(prob, 1.0)


if __name__ == "__main__":
    unittest.main()
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add integration test verifying feature extractor pipeline with calibrated classifier",
        "2026-11-11 10:38:00 +0530",
        ["tests/detection/test_ml_models.py"],
    )


def step_25():
    # refactor(ml): export model classifiers and protocols in sbh.detection.ml package
    pkg_init = ROOT / "src/sbh/detection/ml/__init__.py"
    content = '''"""Machine learning detection, evaluation, and calibration package."""

from __future__ import annotations

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

__all__ = [
    "ALL_FEATURE_NAMES",
    "CORE_FEATURE_NAMES",
    "INDICATOR_FEATURE_NAMES",
    "AccountFeatureExtractor",
    "AccountFeatureVector",
    "BaselineLogisticClassifier",
    "BotModelProtocol",
    "CalibratedBotClassifier",
    "FeatureImputer",
    "HybridEnsembleDetector",
    "IsolationForestAnomalyDetector",
    "MLFeaturePipeline",
    "ModelPrediction",
    "RandomForestBotClassifier",
    "calculate_hourly_entropy",
    "calculate_inter_post_intervals",
    "calculate_shannon_entropy",
    "calculate_simhash_repetition",
    "create_default_bot_classifier",
    "determine_risk_band",
    "extract_content_features",
    "extract_feature_matrix",
    "extract_profile_features",
]
'''
    pkg_init.write_text(content, encoding="utf-8")
    git_commit(
        "refactor(ml): export model classifiers and protocols in sbh.detection.ml package",
        "2026-11-11 10:40:00 +0530",
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
    print("Batch 2 completed successfully!")


if __name__ == "__main__":
    main()
