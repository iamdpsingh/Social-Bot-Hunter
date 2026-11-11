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


class ModelRegistry:
    """Singleton manager caching loaded model artifacts in memory."""

    _instance: ModelRegistry | None = None

    def __init__(self, models_dir: Path | None = None) -> None:
        self.models_dir = models_dir or (Path(__file__).resolve().parents[4] / "data" / "models")
        self._cached_model: Any | None = None
        self._cached_imputer: FeatureImputer | None = None
        self._cached_meta: ModelArtifactMetadata | None = None

    @classmethod
    def get_instance(cls, models_dir: Path | None = None) -> ModelRegistry:
        if cls._instance is None:
            cls._instance = cls(models_dir)
        return cls._instance

    def get_default_model(self) -> tuple[Any, FeatureImputer, ModelArtifactMetadata]:
        """Retrieve or lazily load the default production model bundle."""
        if self._cached_model is None:
            weights_file = self.models_dir / "classifier_v1.joblib"
            if not weights_file.exists():
                # Auto-train baseline if artifact does not exist
                self._train_and_save_fallback()
            model, imputer, meta = load_model_bundle(self.models_dir, "classifier_v1", verify_checksum=True)
            self._cached_model = model
            self._cached_imputer = imputer
            self._cached_meta = meta
        assert self._cached_imputer is not None
        assert self._cached_meta is not None
        return self._cached_model, self._cached_imputer, self._cached_meta

    def _train_and_save_fallback(self) -> None:
        """Train and persist baseline model artifact on initial setup."""
        from sbh.detection.ml.benchmark import generate_benchmark_dataset
        from sbh.detection.ml.features import MLFeaturePipeline
        from sbh.detection.ml.metrics import compute_evaluation_metrics
        from sbh.detection.ml.models import create_default_bot_classifier

        ds = generate_benchmark_dataset(n_benign=100, n_bots=100, n_campaigns=10, random_seed=42)
        pipeline = MLFeaturePipeline().fit(ds.accounts, ds.contents_map)
        matrix = [pipeline.transform_one(acc, ds.contents_map.get(acc["account_id"])) for acc in ds.accounts]

        model = create_default_bot_classifier(random_state=42)
        model.fit(matrix, ds.labels)

        y_prob = model.predict_proba(matrix)
        y_pred = model.predict(matrix)
        metrics = compute_evaluation_metrics(ds.labels, y_pred, y_prob)

        meta_dict = {
            "model_version": "v1.0.0",
            "algorithm": "CalibratedClassifierCV(RandomForestClassifier)",
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "training_samples": len(ds.accounts),
            "metrics": {
                "f1": metrics.f1,
                "pr_auc": metrics.pr_auc,
                "roc_auc": metrics.roc_auc,
                "brier_score": metrics.brier_score,
                "ece": metrics.ece,
                "accuracy": metrics.accuracy,
            },
            "feature_names": list(ALL_FEATURE_NAMES),
            "author": "dpsingh",
            "description": "Default pre-trained calibrated bot detector ensemble",
        }
        save_model_bundle(model, pipeline.imputer, meta_dict, self.models_dir, "classifier_v1")

    def reload(self) -> None:
        """Clear in-memory cache forcing reload from disk."""
        self._cached_model = None
        self._cached_imputer = None
        self._cached_meta = None
