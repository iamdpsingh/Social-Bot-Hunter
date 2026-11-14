"""Granular benchmark test 4: SLA failure detection."""

from __future__ import annotations

import time
import unittest

from sbh.benchmarks.runner import BenchmarkHarness


class TestBenchGranularB204(unittest.TestCase):
    def test_sla_failure_recorded(self):
        harness = BenchmarkHarness(warmup_runs=0)

        def slow_op():
            time.sleep(0.005)  # 5 ms

        result = harness.run_callable("slow_op", slow_op, iterations=3, sla_p99_ms=1.0)
        self.assertFalse(result.passed_sla)


if __name__ == "__main__":
    unittest.main()
