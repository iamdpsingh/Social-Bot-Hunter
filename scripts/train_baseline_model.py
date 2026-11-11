#!/usr/bin/env python3
"""Train baseline production bot detection model and serialize to data/models/."""

from datetime import UTC, datetime
from pathlib import Path

from sbh.detection.ml.benchmark import generate_benchmark_dataset
from sbh.detection.ml.features import ALL_FEATURE_NAMES, MLFeaturePipeline
from sbh.detection.ml.metrics import compute_evaluation_metrics
from sbh.detection.ml.models import create_default_bot_classifier
from sbh.detection.ml.serialization import save_model_bundle


def main():
    root = Path(__file__).resolve().parents[1]
    output_dir = root / "data" / "models"
    print("Generating benchmark training dataset...")
    ds = generate_benchmark_dataset(n_benign=150, n_bots=150, n_campaigns=15, random_seed=42)

    print("Fitting feature extraction pipeline...")
    pipeline = MLFeaturePipeline().fit(ds.accounts, ds.contents_map)
    X = [pipeline.transform_one(acc, ds.contents_map.get(acc["account_id"])) for acc in ds.accounts]

    print("Training CalibratedBotClassifier...")
    model = create_default_bot_classifier(random_state=42)
    model.fit(X, ds.labels)

    y_prob = model.predict_proba(X)
    y_pred = model.predict(X)
    metrics = compute_evaluation_metrics(ds.labels, y_pred, y_prob)

    meta_dict = {
        "model_version": "v1.0.0",
        "algorithm": "CalibratedClassifierCV(RandomForestClassifier)",
        "trained_at": datetime.now(UTC).isoformat(),
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
        "description": "Production calibrated bot detector ensemble v1.0.0",
    }

    w_path, m_path = save_model_bundle(model, pipeline.imputer, meta_dict, output_dir, "classifier_v1")
    print(f"Model saved to {w_path} and metadata to {m_path}")
    print(f"Metrics: F1={metrics.f1}, PR-AUC={metrics.pr_auc}, Brier={metrics.brier_score}")


if __name__ == "__main__":
    main()
