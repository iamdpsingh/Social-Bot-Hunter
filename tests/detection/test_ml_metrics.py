"""Unit tests for ML evaluation metrics, calibration curves, and ECE diagnostics."""

import unittest
import numpy as np
from sbh.detection.ml.metrics import (
    compute_evaluation_metrics,
    compute_calibration_curve,
    compute_expected_calibration_error,
    EvaluationMetrics,
    CalibrationCurvePoint,
)


class TestMetricsCalculation(unittest.TestCase):
    def test_perfect_predictions(self):
        y_true = [0, 0, 1, 1]
        y_pred = [0, 0, 1, 1]
        y_prob = [0.05, 0.10, 0.90, 0.95]

        m = compute_evaluation_metrics(y_true, y_pred, y_prob)
        self.assertEqual(m.precision, 1.0)
        self.assertEqual(m.recall, 1.0)
        self.assertEqual(m.f1, 1.0)
        self.assertEqual(m.accuracy, 1.0)
        self.assertEqual(m.confusion_matrix["tp"], 2)
        self.assertEqual(m.confusion_matrix["tn"], 2)
        self.assertEqual(m.confusion_matrix["fp"], 0)
        self.assertEqual(m.confusion_matrix["fn"], 0)
