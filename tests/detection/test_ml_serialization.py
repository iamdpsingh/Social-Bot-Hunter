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


    def test_sha256_computation(self):
        fpath = self.model_dir / "sample.txt"
        fpath.write_text("social-bot-hunter-test-content", encoding="utf-8")
        h1 = compute_file_sha256(fpath)
        h2 = compute_file_sha256(fpath)
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 64)


    def test_checksum_tampering_detection(self):
        X = [[float(i)] * 44 for i in range(10)]
        y = [0] * 5 + [1] * 5
        model = BaselineLogisticClassifier().fit(X, y)
        imputer = FeatureImputer()
        imputer.is_fitted = True

        w_path, _ = save_model_bundle(model, imputer, {}, self.model_dir, "tamper_test")

        # Corrupt file contents by appending random bytes
        with open(w_path, "ab") as f:
            f.write(b"CORRUPTED_BYTES")

        with self.assertRaises(ModelIntegrityError):
            load_model_bundle(self.model_dir, "tamper_test", verify_checksum=True)


    def test_schema_mismatch_error(self):
        X = [[float(i)] * 44 for i in range(10)]
        y = [0] * 5 + [1] * 5
        model = BaselineLogisticClassifier().fit(X, y)
        imputer = FeatureImputer()
        imputer.is_fitted = True

        meta = {"feature_names": ["f1", "f2"]}  # Only 2 features instead of 44
        save_model_bundle(model, imputer, meta, self.model_dir, "schema_test")

        with self.assertRaises(ModelSchemaError):
            load_model_bundle(self.model_dir, "schema_test", verify_checksum=False)
