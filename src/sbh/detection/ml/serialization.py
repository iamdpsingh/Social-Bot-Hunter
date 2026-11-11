"""Model serialization, artifact persistence, and integrity verification."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib

from sbh.detection.ml.features import ALL_FEATURE_NAMES, FeatureImputer


class ModelIntegrityError(Exception):
    """Raised when model artifact checksum verification fails."""


class ModelSchemaError(Exception):
    """Raised when model feature schema is incompatible with runtime expectations."""


@dataclass
class ModelArtifactMetadata:
    """Metadata specification accompanying serialized ML model weights."""

    model_version: str
    algorithm: str
    trained_at: str
    training_samples: int
    metrics: dict[str, float]
    feature_names: list[str]
    sha256_checksum: str
    author: str = "dpsingh"
    description: str = "Social Bot Hunter calibrated bot detection ensemble"
