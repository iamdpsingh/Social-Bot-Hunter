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
