"""FastAPI router for ML bot detection, model governance, and calibration diagnostics."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from sbh.detection.ml.explain import ModelExplainer
from sbh.detection.ml.features import AccountFeatureExtractor
from sbh.detection.ml.metrics import compute_calibration_curve
from sbh.detection.ml.models import HybridEnsembleDetector
from sbh.detection.ml.serialization import ModelRegistry
from services.api.auth import get_current_user
from services.api.dependencies import get_audit_repo
from services.api.models import User
from services.api.schemas import (
    CalibrationCurveResponse,
    CalibrationPointItem,
    FeatureImportanceResponse,
    MLFeatureAttributionItem,
    MLModelInfoResponse,
    MLPredictRequest,
    MLPredictResponse,
)

router = APIRouter()


@router.get("/model", response_model=MLModelInfoResponse, summary="Get registered ML model metadata")
def get_model_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> MLModelInfoResponse:
    """Retrieve metadata, training sample size, and performance metrics for active classifier."""
    registry = ModelRegistry.get_instance()
    _, _, meta = registry.get_default_model()
    return MLModelInfoResponse(
        model_version=meta.model_version,
        algorithm=meta.algorithm,
        trained_at=meta.trained_at,
        training_samples=meta.training_samples,
        metrics=meta.metrics,
        feature_count=len(meta.feature_names),
        sha256_checksum=meta.sha256_checksum,
        author=meta.author,
        description=meta.description,
    )
