"""Unit tests for ML local explainability and feature attributions."""

import unittest
import numpy as np
from sbh.detection.ml.explain import (
    ModelExplainer,
    FeatureAttribution,
    PredictionExplanation,
    describe_feature_impact,
    explanation_to_dict,
)
from sbh.detection.ml.features import ALL_FEATURE_NAMES
from sbh.detection.ml.models import BaselineLogisticClassifier, RandomForestBotClassifier, CalibratedBotClassifier


class TestDescribeFeatureImpact(unittest.TestCase):
    def test_missing_feature_description(self):
        desc = describe_feature_impact("followers_count", 0.0, True, is_missing=True)
        self.assertIn("Data was unavailable", desc)

    def test_simhash_duplicate_description(self):
        desc_pos = describe_feature_impact("simhash_duplicate_ratio", 0.8, is_positive=True, is_missing=False)
        self.assertIn("near-duplicate", desc_pos)
        desc_neg = describe_feature_impact("simhash_duplicate_ratio", 0.0, is_positive=False, is_missing=False)
        self.assertIn("Diverse", desc_neg)


class TestModelExplainerLogistic(unittest.TestCase):
    def test_explain_linear_model(self):
        X = np.random.randn(40, 44)
        y = np.array([0] * 20 + [1] * 20)
        clf = BaselineLogisticClassifier().fit(X, y)

        explainer = ModelExplainer()
        exp = explainer.explain_prediction("target_user", list(X[0]), clf, top_k=3)

        self.assertEqual(exp.account_id, "target_user")
        self.assertGreaterEqual(exp.bot_probability, 0.0)
        self.assertLessEqual(exp.bot_probability, 1.0)
        self.assertLessEqual(len(exp.top_positive_drivers), 3)
        self.assertLessEqual(len(exp.top_negative_drivers), 3)
        self.assertGreater(len(exp.global_feature_importances), 0)
