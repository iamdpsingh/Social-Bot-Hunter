"""Granular benchmark test 4: SLA failure detection."""

from __future__ import annotations

import unittest
from sbh.benchmarks.runner import BenchmarkHarness


class TestBenchGranularB204(unittest.TestCase):
    def test_sla_failure_recorded(self):
        harness = BenchmarkHarness(warmup_runs=0)
        # Function with SLA 0.0001 ms will fail
        result = harness.run_callable("fast_op", lambda: None, iterations=10, sla_p99_ms=0.000001)
        self.assertFalse(result.passed_sla)


if __name__ == "__main__":
    unittest.main()
