"""Granular benchmark test 7: json round-trip."""

from __future__ import annotations

import json
import unittest

from sbh.benchmarks.metrics import BenchmarkMetrics
from sbh.benchmarks.reporter import BenchmarkReportGenerator
from sbh.benchmarks.runner import BenchmarkTaskResult


class TestBenchGranularB207(unittest.TestCase):
    def test_json_structure_keys(self):
        m = BenchmarkMetrics.from_durations("task_a", [2.0])
        res = BenchmarkTaskResult("task_a", m, True, 10.0)
        js = BenchmarkReportGenerator.to_json([res])
        parsed = json.loads(js)[0]
        self.assertEqual(parsed["metrics"]["p50_ms"], 2.0)
        self.assertTrue(parsed["passed_sla"])


if __name__ == "__main__":
    unittest.main()
