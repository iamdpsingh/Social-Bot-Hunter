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
