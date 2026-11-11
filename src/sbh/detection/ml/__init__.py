"""Machine learning detection, evaluation, and calibration package."""

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
