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
