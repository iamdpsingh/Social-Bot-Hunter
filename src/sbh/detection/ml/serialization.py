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


def compute_file_sha256(filepath: Path) -> str:
    """Compute SHA-256 hexadecimal digest of file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def save_model_bundle(
    model: Any,
    imputer: FeatureImputer,
    metadata_dict: dict[str, Any],
    output_dir: Path,
    base_name: str = "classifier_v1",
) -> tuple[Path, Path]:
    """Serialize model and imputer with compression, computing SHA-256 checksum and writing metadata."""
    output_dir.mkdir(parents=True, exist_ok=True)
    weights_path = output_dir / f"{base_name}.joblib"
    meta_path = output_dir / f"{base_name}.json"

    bundle = {
        "model": model,
        "imputer": imputer,
        "serialized_at": datetime.now(timezone.utc).isoformat(),
    }
    joblib.dump(bundle, weights_path, compress=3)

    checksum = compute_file_sha256(weights_path)
    metadata = ModelArtifactMetadata(
        model_version=metadata_dict.get("model_version", "v1.0.0"),
        algorithm=metadata_dict.get("algorithm", str(type(model).__name__)),
        trained_at=metadata_dict.get("trained_at", datetime.now(timezone.utc).isoformat()),
        training_samples=int(metadata_dict.get("training_samples", 0)),
        metrics=metadata_dict.get("metrics", {}),
        feature_names=metadata_dict.get("feature_names", list(ALL_FEATURE_NAMES)),
        sha256_checksum=checksum,
        author=metadata_dict.get("author", "dpsingh"),
        description=metadata_dict.get("description", "Calibrated bot detector"),
    )

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(asdict(metadata), f, indent=2)

    return weights_path, meta_path


def load_model_bundle(
    model_dir: Path,
    base_name: str = "classifier_v1",
    verify_checksum: bool = True,
) -> tuple[Any, FeatureImputer, ModelArtifactMetadata]:
    """Load and verify serialized model bundle."""
    weights_path = model_dir / f"{base_name}.joblib"
    meta_path = model_dir / f"{base_name}.json"

    if not weights_path.exists():
        raise FileNotFoundError(f"Model weights file not found: {weights_path}")
    if not meta_path.exists():
        raise FileNotFoundError(f"Model metadata file not found: {meta_path}")

    with open(meta_path, encoding="utf-8") as f:
        raw_meta = json.load(f)

    meta = ModelArtifactMetadata(**raw_meta)

    if verify_checksum:
        actual_checksum = compute_file_sha256(weights_path)
        if actual_checksum != meta.sha256_checksum:
            raise ModelIntegrityError(
                f"Model weights checksum mismatch! Expected {meta.sha256_checksum}, got {actual_checksum}"
            )

    # Validate feature names length
    if len(meta.feature_names) != len(ALL_FEATURE_NAMES):
        raise ModelSchemaError(
            f"Feature count mismatch: bundle has {len(meta.feature_names)}, runtime expects {len(ALL_FEATURE_NAMES)}"
        )

    bundle = joblib.load(weights_path)
    return bundle["model"], bundle["imputer"], meta
