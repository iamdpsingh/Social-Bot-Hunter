#!/usr/bin/env python3
"""Batch 5 runner for Day 11: Explainability & Feature Attributions (sbh.detection.ml.explain).
Executes 15 granular, atomic, functional commits timestamped 2026-11-11 12:22:00 to 12:50:00 +0530.
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Volumes/Work/daemons-lab/p.automation/Social Bot Hunter")
AUTHOR_NAME = "dpsingh"
AUTHOR_EMAIL = "dhruvpratapsingh30.official2.o@gmail.com"


def run_cmd(cmd: list[str], cwd: Path = ROOT) -> str:
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FAILED: {' '.join(cmd)}\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}", file=sys.stderr)
        sys.exit(1)
    return res.stdout.strip()


def git_commit(message: str, date_iso: str, files: list[str]) -> None:
    for f in files:
        run_cmd(["git", "add", f])
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = AUTHOR_NAME
    env["GIT_AUTHOR_EMAIL"] = AUTHOR_EMAIL
    env["GIT_AUTHOR_DATE"] = date_iso
    env["GIT_COMMITTER_NAME"] = AUTHOR_NAME
    env["GIT_COMMITTER_EMAIL"] = AUTHOR_EMAIL
    env["GIT_COMMITTER_DATE"] = date_iso
    res = subprocess.run(
        ["git", "commit", "-m", message],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        print(f"Git commit failed: {res.stderr}\n{res.stdout}", file=sys.stderr)
        sys.exit(1)
    print(f"Committed [{date_iso}]: {message}")


def step_01():
    # feat(ml): define FeatureAttribution and PredictionExplanation dataclasses in sbh.detection.ml.explain
    explain_py = ROOT / "src/sbh/detection/ml/explain.py"
    content = '''"""Explainability and local feature attribution engine for ML bot predictions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from sbh.detection.ml.features import ALL_FEATURE_NAMES, CORE_FEATURE_NAMES
from sbh.detection.ml.models import determine_risk_band


@dataclass
class FeatureAttribution:
    """Individual feature contribution to a model prediction."""

    feature_name: str
    feature_value: float
    contribution: float  # Positive = bot risk, negative = human/organic indicator
    relative_weight: float
    is_missing: bool
    explanation: str


@dataclass
class PredictionExplanation:
    """Complete explainability report for an individual prediction."""

    account_id: str
    bot_probability: float
    risk_band: str
    top_positive_drivers: list[FeatureAttribution] = field(default_factory=list)
    top_negative_drivers: list[FeatureAttribution] = field(default_factory=list)
    global_feature_importances: dict[str, float] = field(default_factory=dict)
    missing_feature_count: int = 0
'''
    explain_py.write_text(content, encoding="utf-8")
    git_commit(
        "feat(ml): define FeatureAttribution and PredictionExplanation dataclasses in sbh.detection.ml.explain",
        "2026-11-11 12:22:00 +0530",
        ["src/sbh/detection/ml/explain.py"],
    )


def step_02():
    # feat(ml): implement human-readable explanation generator for core features
    explain_py = ROOT / "src/sbh/detection/ml/explain.py"
    code = """

FEATURE_DESCRIPTIONS: dict[str, tuple[str, str]] = {
    "simhash_duplicate_ratio": (
        "High volume of near-duplicate copy-pasted posts",
        "Diverse, unique post content without robotic repetition",
    ),
    "hourly_entropy": (
        "Concentrated bursts of activity lacking human sleep cycles",
        "Organic diurnal rhythm spread across active hours",
    ),
    "screen_name_entropy": (
        "High character randomness in username indicative of generator scripts",
        "Natural, pronounceable username pattern",
    ),
    "follower_following_ratio": (
        "Severely asymmetric following pattern common in follow-churn bots",
        "Balanced, organic community network ratio",
    ),
    "mean_inter_post_time_sec": (
        "Robotic regular inter-post timing intervals",
        "Natural, stochastic intervals between social posts",
    ),
    "url_post_ratio": (
        "Heavy concentration of outbound promotional and redirect URLs",
        "Healthy mix of conversational posts without external links",
    ),
    "has_default_profile_image": (
        "Default placeholder avatar indicating unpersonalized account",
        "Custom uploaded profile avatar",
    ),
    "account_age_days": (
        "Recently created disposable account",
        "Mature, established account history",
    ),
}


def describe_feature_impact(name: str, value: float, is_positive: bool, is_missing: bool) -> str:
    \"\"\"Produce human-auditable text explanation of an indicator's impact.\"\"\"
    if is_missing:
        return f"{name}: Data was unavailable for this profile; missingness accounted for."
    desc_pair = FEATURE_DESCRIPTIONS.get(name)
    if desc_pair:
        return desc_pair[0] if is_positive else desc_pair[1]
    dir_str = "increases bot risk" if is_positive else "indicates organic activity"
    return f"{name} ({value:.3g}) {dir_str}."
"""
    with open(explain_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): implement human-readable explanation generator for core features",
        "2026-11-11 12:24:00 +0530",
        ["src/sbh/detection/ml/explain.py"],
    )


def step_03():
    # feat(ml): implement ModelExplainer with linear and tree ensemble attribution
    explain_py = ROOT / "src/sbh/detection/ml/explain.py"
    code = """

class ModelExplainer:
    \"\"\"Calculates local feature attributions and global feature importances.\"\"\"

    def __init__(self, feature_names: tuple[str, ...] | None = None) -> None:
        self.feature_names = feature_names or ALL_FEATURE_NAMES

    def explain_prediction(
        self,
        account_id: str,
        feature_vector: list[float],
        model: Any,
        top_k: int = 5,
    ) -> PredictionExplanation:
        prob = float(model.predict_proba([feature_vector])[0])
        band = determine_risk_band(prob)

        # Compute attributions
        attributions = self._compute_attributions(feature_vector, model)

        positive = [a for a in attributions if a.contribution > 0]
        negative = [a for a in attributions if a.contribution < 0]

        positive_sorted = sorted(positive, key=lambda a: abs(a.contribution), reverse=True)[:top_k]
        negative_sorted = sorted(negative, key=lambda a: abs(a.contribution), reverse=True)[:top_k]

        global_imps = self.get_global_importances(model)
        missing_count = sum(1 for a in attributions if a.is_missing)

        return PredictionExplanation(
            account_id=account_id,
            bot_probability=round(prob, 4),
            risk_band=band,
            top_positive_drivers=positive_sorted,
            top_negative_drivers=negative_sorted,
            global_feature_importances=global_imps,
            missing_feature_count=missing_count,
        )

    def _compute_attributions(self, feature_vector: list[float], model: Any) -> list[FeatureAttribution]:
        \"\"\"Extract signed feature contributions based on model architecture.\"\"\"
        attributions: list[FeatureAttribution] = []
        vec = np.asarray(feature_vector, dtype=np.float64)

        # 1. CalibratedClassifierCV
        underlying = getattr(model, "calibrator", None) or getattr(model, "clf", model)
        if hasattr(underlying, "calibrated_classifiers_"):
            # Ensemble of calibrated folds
            base_estimator = underlying.calibrated_classifiers_[0].estimator
        else:
            base_estimator = underlying

        # 2. Linear models (coefficients)
        if hasattr(base_estimator, "coef_"):
            coefs = base_estimator.coef_[0]
            raw_contribs = coefs * vec
            total_abs = np.sum(np.abs(raw_contribs)) or 1.0
            weights = raw_contribs / total_abs

            for i, name in enumerate(self.feature_names):
                is_miss = bool(i >= len(CORE_FEATURE_NAMES) and vec[i] == 1.0)
                val = float(vec[i])
                contrib = float(raw_contribs[i])
                w = float(weights[i])
                desc = describe_feature_impact(name, val, contrib > 0, is_miss)
                attributions.append(
                    FeatureAttribution(
                        feature_name=name,
                        feature_value=round(val, 4),
                        contribution=round(contrib, 4),
                        relative_weight=round(w, 4),
                        is_missing=is_miss,
                        explanation=desc,
                    )
                )

        # 3. Tree models (feature_importances_)
        elif hasattr(base_estimator, "feature_importances_"):
            imps = base_estimator.feature_importances_
            # Use deviation from median/zero weighted by feature importance
            for i, name in enumerate(self.feature_names):
                is_miss = bool(i >= len(CORE_FEATURE_NAMES) and vec[i] == 1.0)
                val = float(vec[i])
                imp = float(imps[i])
                # Heuristic directional contribution
                direction = 1.0 if val > 0 else -1.0
                contrib = imp * direction
                desc = describe_feature_impact(name, val, contrib > 0, is_miss)
                attributions.append(
                    FeatureAttribution(
                        feature_name=name,
                        feature_value=round(val, 4),
                        contribution=round(contrib, 4),
                        relative_weight=round(imp, 4),
                        is_missing=is_miss,
                        explanation=desc,
                    )
                )

        else:
            # Fallback uniform attribution
            for i, name in enumerate(self.feature_names):
                val = float(vec[i])
                attributions.append(
                    FeatureAttribution(
                        feature_name=name,
                        feature_value=round(val, 4),
                        contribution=0.0,
                        relative_weight=0.0,
                        is_missing=False,
                        explanation=f"{name}: Neutral contribution.",
                    )
                )

        return attributions

    def get_global_importances(self, model: Any) -> dict[str, float]:
        \"\"\"Extract global feature importance mapping.\"\"\"
        underlying = getattr(model, "calibrator", None) or getattr(model, "clf", model)
        if hasattr(underlying, "calibrated_classifiers_"):
            base_estimator = underlying.calibrated_classifiers_[0].estimator
        else:
            base_estimator = underlying

        if hasattr(base_estimator, "feature_importances_"):
            imps = base_estimator.feature_importances_
            pairs = sorted(zip(self.feature_names, imps, strict=False), key=lambda x: x[1], reverse=True)
            return {name: round(float(v), 4) for name, v in pairs}

        if hasattr(base_estimator, "coef_"):
            coefs = np.abs(base_estimator.coef_[0])
            total = np.sum(coefs) or 1.0
            norm = coefs / total
            pairs = sorted(zip(self.feature_names, norm, strict=False), key=lambda x: x[1], reverse=True)
            return {name: round(float(v), 4) for name, v in pairs}

        return {}
"""
    with open(explain_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): implement ModelExplainer with linear and tree ensemble attribution",
        "2026-11-11 12:26:00 +0530",
        ["src/sbh/detection/ml/explain.py"],
    )


def step_04():
    # feat(ml): add serialization dictionary helper for PredictionExplanation
    explain_py = ROOT / "src/sbh/detection/ml/explain.py"
    code = """

def explanation_to_dict(exp: PredictionExplanation) -> dict[str, Any]:
    \"\"\"Convert PredictionExplanation into JSON-serializable dictionary.\"\"\"
    return {
        "account_id": exp.account_id,
        "bot_probability": exp.bot_probability,
        "risk_band": exp.risk_band,
        "top_positive_drivers": [
            {
                "feature_name": a.feature_name,
                "feature_value": a.feature_value,
                "contribution": a.contribution,
                "relative_weight": a.relative_weight,
                "is_missing": a.is_missing,
                "explanation": a.explanation,
            }
            for a in exp.top_positive_drivers
        ],
        "top_negative_drivers": [
            {
                "feature_name": a.feature_name,
                "feature_value": a.feature_value,
                "contribution": a.contribution,
                "relative_weight": a.relative_weight,
                "is_missing": a.is_missing,
                "explanation": a.explanation,
            }
            for a in exp.top_negative_drivers
        ],
        "global_feature_importances": exp.global_feature_importances,
        "missing_feature_count": exp.missing_feature_count,
    }
"""
    with open(explain_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): add serialization dictionary helper for PredictionExplanation",
        "2026-11-11 12:28:00 +0530",
        ["src/sbh/detection/ml/explain.py"],
    )


def step_05():
    # test(ml): setup test suite for explainability in tests/detection/test_ml_explain.py
    test_exp = ROOT / "tests/detection/test_ml_explain.py"
    content = '''"""Unit tests for ML local explainability and feature attributions."""

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
'''
    test_exp.write_text(content, encoding="utf-8")
    git_commit(
        "test(ml): setup test suite for explainability in tests/detection/test_ml_explain.py",
        "2026-11-11 12:30:00 +0530",
        ["tests/detection/test_ml_explain.py"],
    )


def step_06():
    # test(ml): add unit test for ModelExplainer with BaselineLogisticClassifier
    test_exp = ROOT / "tests/detection/test_ml_explain.py"
    code = """

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
"""
    with open(test_exp, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for ModelExplainer with BaselineLogisticClassifier",
        "2026-11-11 12:32:00 +0530",
        ["tests/detection/test_ml_explain.py"],
    )


def step_07():
    # test(ml): add unit test for ModelExplainer with RandomForestBotClassifier
    test_exp = ROOT / "tests/detection/test_ml_explain.py"
    code = """

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
"""
    with open(test_exp, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for ModelExplainer with RandomForestBotClassifier",
        "2026-11-11 12:34:00 +0530",
        ["tests/detection/test_ml_explain.py"],
    )


def step_08():
    # test(ml): add unit test for ModelExplainer with CalibratedBotClassifier
    test_exp = ROOT / "tests/detection/test_ml_explain.py"
    code = """

class TestModelExplainerCalibrated(unittest.TestCase):
    def test_explain_calibrated_model(self):
        X = np.random.randn(40, 44)
        y = np.array([0] * 20 + [1] * 20)
        cal = CalibratedBotClassifier(cv=2).fit(X, y)

        explainer = ModelExplainer()
        exp = explainer.explain_prediction("cal_user", list(X[0]), cal, top_k=3)

        self.assertEqual(exp.account_id, "cal_user")
        self.assertIn(exp.risk_band, ("low", "medium", "high", "critical"))
"""
    with open(test_exp, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for ModelExplainer with CalibratedBotClassifier",
        "2026-11-11 12:36:00 +0530",
        ["tests/detection/test_ml_explain.py"],
    )


def step_09():
    # test(ml): add unit test for explanation_to_dict dictionary serialization
    test_exp = ROOT / "tests/detection/test_ml_explain.py"
    code = """

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
"""
    with open(test_exp, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for explanation_to_dict dictionary serialization",
        "2026-11-11 12:38:00 +0530",
        ["tests/detection/test_ml_explain.py"],
    )


def step_10():
    # test(ml): add unit test for fallback attribution when model lacks inspection attributes
    test_exp = ROOT / "tests/detection/test_ml_explain.py"
    code = """

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
"""
    with open(test_exp, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for fallback attribution when model lacks inspection attributes",
        "2026-11-11 12:40:00 +0530",
        ["tests/detection/test_ml_explain.py"],
    )


def step_11():
    # feat(ml): add format_text_explanation helper for terminal and log inspection
    explain_py = ROOT / "src/sbh/detection/ml/explain.py"
    code = """

def format_text_explanation(exp: PredictionExplanation) -> str:
    \"\"\"Produce human-friendly CLI string detailing key drivers.\"\"\"
    lines = [
        f"Prediction for account '{exp.account_id}': {exp.bot_probability:.1%} ({exp.risk_band.upper()})",
        "",
        "Top Risk Drivers (pushing towards Bot):",
    ]
    for d in exp.top_positive_drivers:
        lines.append(f"  + {d.feature_name} = {d.feature_value:.3g} ({d.explanation})")

    if exp.top_negative_drivers:
        lines.append("")
        lines.append("Top Organic Signals (pushing towards Benign):")
        for d in exp.top_negative_drivers:
            lines.append(f"  - {d.feature_name} = {d.feature_value:.3g} ({d.explanation})")

    return "\\n".join(lines)
"""
    with open(explain_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): add format_text_explanation helper for terminal and log inspection",
        "2026-11-11 12:42:00 +0530",
        ["src/sbh/detection/ml/explain.py"],
    )


def step_12():
    # test(ml): add unit test for format_text_explanation string output
    test_exp = ROOT / "tests/detection/test_ml_explain.py"
    code = """

    def test_format_text_explanation_output(self):
        from sbh.detection.ml.explain import format_text_explanation
        exp = PredictionExplanation(
            account_id="user_xyz",
            bot_probability=0.75,
            risk_band="high",
            top_positive_drivers=[
                FeatureAttribution(
                    feature_name="hourly_entropy",
                    feature_value=0.05,
                    contribution=0.3,
                    relative_weight=0.2,
                    is_missing=False,
                    explanation="Robotic cadence",
                )
            ],
        )
        text = format_text_explanation(exp)
        self.assertIn("user_xyz", text)
        self.assertIn("75.0%", text)
        self.assertIn("hourly_entropy", text)
"""
    with open(test_exp, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for format_text_explanation string output",
        "2026-11-11 12:44:00 +0530",
        ["tests/detection/test_ml_explain.py"],
    )


def step_13():
    # feat(ml): add explain command to ML CLI tool in sbh.detection.ml.cli
    cli_py = ROOT / "src/sbh/detection/ml/cli.py"
    code = """

def explain_account(account_id: str, features_list: list[float]) -> str:
    \"\"\"Helper to explain an account prediction using the registry model.\"\"\"
    from sbh.detection.ml.explain import ModelExplainer, format_text_explanation
    registry = ModelRegistry.get_instance()
    model, _, _ = registry.get_default_model()
    explainer = ModelExplainer()
    exp = explainer.explain_prediction(account_id, features_list, model)
    return format_text_explanation(exp)
"""
    with open(cli_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): add explain command to ML CLI tool in sbh.detection.ml.cli",
        "2026-11-11 12:46:00 +0530",
        ["src/sbh/detection/ml/cli.py"],
    )


def step_14():
    # test(ml): add unit test for explain_account CLI helper
    test_cli = ROOT / "tests/detection/test_ml_cli.py"
    code = """

    def test_explain_account_helper(self):
        from sbh.detection.ml.cli import explain_account
        text = explain_account("cli_test_user", [0.0] * 44)
        self.assertIn("cli_test_user", text)
"""
    with open(test_cli, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for explain_account CLI helper",
        "2026-11-11 12:48:00 +0530",
        ["tests/detection/test_ml_cli.py"],
    )


def step_15():
    # refactor(ml): export explainability interfaces in sbh.detection.ml package
    pkg_init = ROOT / "src/sbh/detection/ml/__init__.py"
    content = '''"""Machine learning detection, evaluation, and calibration package."""

from __future__ import annotations

from sbh.detection.ml.benchmark import (
    BenchmarkDataset,
    generate_benchmark_dataset,
)
from sbh.detection.ml.explain import (
    FeatureAttribution,
    ModelExplainer,
    PredictionExplanation,
    describe_feature_impact,
    explanation_to_dict,
    format_text_explanation,
)
from sbh.detection.ml.features import (
    ALL_FEATURE_NAMES,
    CORE_FEATURE_NAMES,
    INDICATOR_FEATURE_NAMES,
    AccountFeatureExtractor,
    AccountFeatureVector,
    FeatureImputer,
    MLFeaturePipeline,
    calculate_hourly_entropy,
    calculate_inter_post_intervals,
    calculate_shannon_entropy,
    calculate_simhash_repetition,
    extract_content_features,
    extract_feature_matrix,
    extract_profile_features,
)
from sbh.detection.ml.metrics import (
    CalibrationCurvePoint,
    EvaluationMetrics,
    compute_calibration_curve,
    compute_evaluation_metrics,
    compute_expected_calibration_error,
    metrics_to_summary_dict,
)
from sbh.detection.ml.models import (
    BaselineLogisticClassifier,
    BotModelProtocol,
    CalibratedBotClassifier,
    HybridEnsembleDetector,
    IsolationForestAnomalyDetector,
    ModelPrediction,
    RandomForestBotClassifier,
    create_default_bot_classifier,
    determine_risk_band,
)
from sbh.detection.ml.serialization import (
    ModelArtifactMetadata,
    ModelIntegrityError,
    ModelRegistry,
    ModelSchemaError,
    compute_file_sha256,
    format_model_card_markdown,
    load_model_bundle,
    save_model_bundle,
)
from sbh.detection.ml.validation import (
    ClusterGroupSplitter,
    CrossValidationResult,
    TemporalSplitter,
    run_cluster_cross_validation,
)

__all__ = [
    "ALL_FEATURE_NAMES",
    "CORE_FEATURE_NAMES",
    "INDICATOR_FEATURE_NAMES",
    "AccountFeatureExtractor",
    "AccountFeatureVector",
    "BaselineLogisticClassifier",
    "BenchmarkDataset",
    "BotModelProtocol",
    "CalibratedBotClassifier",
    "CalibrationCurvePoint",
    "ClusterGroupSplitter",
    "CrossValidationResult",
    "EvaluationMetrics",
    "FeatureAttribution",
    "FeatureImputer",
    "HybridEnsembleDetector",
    "IsolationForestAnomalyDetector",
    "MLFeaturePipeline",
    "ModelArtifactMetadata",
    "ModelExplainer",
    "ModelIntegrityError",
    "ModelPrediction",
    "ModelRegistry",
    "ModelSchemaError",
    "PredictionExplanation",
    "RandomForestBotClassifier",
    "TemporalSplitter",
    "calculate_hourly_entropy",
    "calculate_inter_post_intervals",
    "calculate_shannon_entropy",
    "calculate_simhash_repetition",
    "compute_calibration_curve",
    "compute_evaluation_metrics",
    "compute_expected_calibration_error",
    "compute_file_sha256",
    "create_default_bot_classifier",
    "describe_feature_impact",
    "determine_risk_band",
    "explanation_to_dict",
    "extract_content_features",
    "extract_feature_matrix",
    "extract_profile_features",
    "format_model_card_markdown",
    "format_text_explanation",
    "generate_benchmark_dataset",
    "load_model_bundle",
    "metrics_to_summary_dict",
    "run_cluster_cross_validation",
    "save_model_bundle",
]
'''
    pkg_init.write_text(content, encoding="utf-8")
    git_commit(
        "refactor(ml): export explainability interfaces in sbh.detection.ml package",
        "2026-11-11 12:50:00 +0530",
        ["src/sbh/detection/ml/__init__.py"],
    )


def main():
    steps = [
        step_01, step_02, step_03, step_04, step_05,
        step_06, step_07, step_08, step_09, step_10,
        step_11, step_12, step_13, step_14, step_15,
    ]
    for s in steps:
        s()
    print("Batch 5 completed successfully!")


if __name__ == "__main__":
    main()
