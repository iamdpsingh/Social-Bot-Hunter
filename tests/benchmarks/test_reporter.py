"""Tests for BenchmarkReportGenerator markdown and json output."""

from __future__ import annotations

import json
import unittest

from sbh.benchmarks.metrics import BenchmarkMetrics
from sbh.benchmarks.reporter import BenchmarkReportGenerator
from sbh.benchmarks.runner import BenchmarkTaskResult


class TestBenchmarkReporter(unittest.TestCase):
    def test_markdown_and_json_generation(self):
        m = BenchmarkMetrics.from_durations("test_op", [1.0, 2.0, 3.0])
        res = BenchmarkTaskResult("test_op", m, passed_sla=True, sla_p99_ms=10.0)

        md = BenchmarkReportGenerator.to_markdown([res])
        self.assertIn("# Social Bot Hunter - Micro-Benchmark & Latency Report", md)
        self.assertIn("`test_op`", md)
        self.assertIn("PASS", md)

        js = BenchmarkReportGenerator.to_json([res])
        data = json.loads(js)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["task_name"], "test_op")
        self.assertTrue(data[0]["passed_sla"])


if __name__ == "__main__":
    unittest.main()
