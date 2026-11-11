"""Machine learning classification, anomaly detection, and probability calibration models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
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


def determine_risk_band(prob: float) -> str:
    """Assign standard 4-tier risk band based on calibrated probability."""
    if prob >= 0.80:
        return "critical"
    if prob >= 0.60:
        return "high"
    if prob >= 0.40:
        return "medium"
    return "low"


class BaselineLogisticClassifier:
    """Interpretable linear baseline using StandardScaler and L2-regularized Logistic Regression."""

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
        """Return learned standardized coefficients for each feature."""
        if not self.is_fitted:
            return {}
        coefs = self.clf.coef_[0]
        return {name: round(float(c), 4) for name, c in zip(feature_names, coefs, strict=False)}


class RandomForestBotClassifier:
    """Non-linear ensemble classifier capturing multi-feature interaction non-linearities."""

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
        """Return MDI (mean decrease in impurity) importances sorted descending."""
        if not self.is_fitted:
            return {}
        imps = self.clf.feature_importances_
        pairs = sorted(zip(feature_names, imps, strict=False), key=lambda x: x[1], reverse=True)
        return {name: round(float(score), 4) for name, score in pairs}


class CalibratedBotClassifier:
    """Probability-calibrated meta-classifier using Platt scaling or isotonic regression."""

    def __init__(
        self,
        base_estimator: Any | None = None,
        method: str = "sigmoid",
        cv: int | str = 3,
    ) -> None:
        self.method = method
        self.cv = cv
        if base_estimator is not None:
            self.base_estimator = base_estimator
        else:
            self.base_estimator = RandomForestClassifier(
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


class IsolationForestAnomalyDetector:
    """Unsupervised outlier detector identifying rare or novel coordinated bot maneuvers."""

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
        """Return normalized anomaly risk score in [0.0, 1.0]. 1.0 = highly anomalous."""
        if not self.is_fitted:
            raise ValueError("IsolationForestAnomalyDetector is not fitted.")
        x_arr = np.asarray(X, dtype=np.float64)
        # raw decision_function: lower means more anomalous (typically in [-0.5, 0.5])
        raw_scores = self.detector.decision_function(x_arr)
        # Invert and normalize: score 0.5 -> 0.0 (normal), score -0.5 -> 1.0 (anomalous)
        normalized = [round(float(min(1.0, max(0.0, 0.5 - s))), 4) for s in raw_scores]
        return normalized

    def predict_outliers(self, X: np.ndarray | list[list[float]]) -> list[bool]:
        """Return True if classified as anomaly / outlier (-1)."""
        if not self.is_fitted:
            raise ValueError("IsolationForestAnomalyDetector is not fitted.")
        x_arr = np.asarray(X, dtype=np.float64)
        preds = self.detector.predict(x_arr)
        return [bool(p == -1) for p in preds]


class HybridEnsembleDetector:
    """Blends explainable heuristic rule score with calibrated ML probability.

    Formula:
        Score_hybrid = 100 * (alpha * prob_ml + (1 - alpha) * (score_rules / 100))
    """

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


def create_default_bot_classifier(random_state: int = 42) -> CalibratedBotClassifier:
    """Factory instantiating production CalibratedBotClassifier with calibrated Random Forest."""
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=4,
        class_weight="balanced",
        random_state=random_state,
        n_jobs=-1,
    )
    return CalibratedBotClassifier(base_estimator=rf, method="sigmoid", cv=3)
