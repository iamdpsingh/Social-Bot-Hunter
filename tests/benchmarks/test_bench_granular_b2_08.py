"""Granular benchmark test 8: SimHash unicode execution."""

from __future__ import annotations

import unittest
from sbh.benchmarks.runner import BenchmarkHarness
from sbh.detection.simhash import compute_simhash


class TestBenchGranularB208(unittest.TestCase):
    def test_unicode_simhash_execution(self):
        harness = BenchmarkHarness(warmup_runs=1)
        res = harness.run_callable("unicode_simhash", lambda: compute_simhash("🚀 日本語テスト ✨"), iterations=20)
        self.assertTrue(res.passed_sla)


if __name__ == "__main__":
    unittest.main()
