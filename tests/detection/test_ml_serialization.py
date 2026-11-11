"""Unit tests for ML model serialization, artifact saving, and checksum validation."""

import json
import tempfile
import unittest
from pathlib import Path
from sbh.detection.ml.features import FeatureImputer, ALL_FEATURE_NAMES
from sbh.detection.ml.models import BaselineLogisticClassifier
from sbh.detection.ml.serialization import (
    save_model_bundle,
    load_model_bundle,
    compute_file_sha256,
    ModelIntegrityError,
    ModelSchemaError,
    ModelRegistry,
)


class TestModelSerialization(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.model_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()


    def test_save_and_load_round_trip(self):
        X = [[float(i)] * 44 for i in range(10)]
        y = [0] * 5 + [1] * 5
        model = BaselineLogisticClassifier().fit(X, y)
        imputer = FeatureImputer()
        imputer.is_fitted = True

        meta = {
            "model_version": "v1.0.0-test",
            "training_samples": 10,
            "metrics": {"f1": 1.0},
        }

        w_path, m_path = save_model_bundle(model, imputer, meta, self.model_dir, "test_model")
        self.assertTrue(w_path.exists())
        self.assertTrue(m_path.exists())

        loaded_model, loaded_imputer, loaded_meta = load_model_bundle(self.model_dir, "test_model")
        self.assertEqual(loaded_meta.model_version, "v1.0.0-test")
        self.assertEqual(loaded_meta.training_samples, 10)

        # Assert identical predictions
        pred_orig = model.predict_proba(X)
        pred_loaded = loaded_model.predict_proba(X)
        self.assertEqual(pred_orig, pred_loaded)
