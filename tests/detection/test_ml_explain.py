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


class TestModelExplainerRandomForest(unittest.TestCase):
    def test_explain_rf_model(self):
        X = np.random.randn(40, 44)
        y = np.array([0] * 20 + [1] * 20)
        rf = RandomForestBotClassifier(n_estimators=10, max_depth=3).fit(X, y)

        explainer = ModelExplainer()
        exp = explainer.explain_prediction("rf_user", list(X[0]), rf, top_k=4)

        self.assertEqual(exp.account_id, "rf_user")
        self.assertLessEqual(len(exp.top_positive_drivers), 4)
        self.assertGreater(len(exp.global_feature_importances), 0)


class TestModelExplainerCalibrated(unittest.TestCase):
    def test_explain_calibrated_model(self):
        X = np.random.randn(40, 44)
        y = np.array([0] * 20 + [1] * 20)
        cal = CalibratedBotClassifier(cv=2).fit(X, y)

        explainer = ModelExplainer()
        exp = explainer.explain_prediction("cal_user", list(X[0]), cal, top_k=3)

        self.assertEqual(exp.account_id, "cal_user")
        self.assertIn(exp.risk_band, ("low", "medium", "high", "critical"))


    def test_explanation_serialization(self):
        exp = PredictionExplanation(
            account_id="acc_123",
            bot_probability=0.88,
            risk_band="critical",
            top_positive_drivers=[
                FeatureAttribution(
                    feature_name="simhash_duplicate_ratio",
                    feature_value=0.9,
                    contribution=0.45,
                    relative_weight=0.5,
                    is_missing=False,
                    explanation="High duplicate posts",
                )
            ],
            top_negative_drivers=[],
            global_feature_importances={"simhash_duplicate_ratio": 0.5},
            missing_feature_count=0,
        )
        d = explanation_to_dict(exp)
        self.assertEqual(d["account_id"], "acc_123")
        self.assertEqual(d["bot_probability"], 0.88)
        self.assertEqual(len(d["top_positive_drivers"]), 1)
        self.assertEqual(d["top_positive_drivers"][0]["feature_name"], "simhash_duplicate_ratio")


class DummyModel:
    def predict_proba(self, X):
        return [0.5]


class TestDummyAttribution(unittest.TestCase):
    def test_dummy_model_fallback(self):
        explainer = ModelExplainer()
        exp = explainer.explain_prediction("dummy", [0.0] * 44, DummyModel())
        self.assertEqual(exp.bot_probability, 0.5)
        self.assertEqual(len(exp.top_positive_drivers), 0)
        self.assertEqual(len(exp.top_negative_drivers), 0)


if __name__ == "__main__":
    unittest.main()
