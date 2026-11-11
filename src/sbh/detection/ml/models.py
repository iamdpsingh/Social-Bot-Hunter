"""Machine learning classification, anomaly detection, and probability calibration models."""

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
