"""Granular benchmark test 12: SLA failure markdown tag."""

from __future__ import annotations

import unittest

from sbh.benchmarks.metrics import BenchmarkMetrics
from sbh.benchmarks.reporter import BenchmarkReportGenerator
from sbh.benchmarks.runner import BenchmarkTaskResult


class TestBenchGranularB212(unittest.TestCase):
    def test_sla_failure_markdown_flag(self):
        m = BenchmarkMetrics.from_durations("slow_task", [100.0])
        res = BenchmarkTaskResult("slow_task", m, passed_sla=False, sla_p99_ms=10.0)
        md = BenchmarkReportGenerator.to_markdown([res])
        self.assertIn("**FAIL**", md)


if __name__ == "__main__":
    unittest.main()
