"""Granular benchmark test 6: markdown table headers."""

from __future__ import annotations

import unittest

from sbh.benchmarks.reporter import BenchmarkReportGenerator


class TestBenchGranularB206(unittest.TestCase):
    def test_empty_results_markdown(self):
        md = BenchmarkReportGenerator.to_markdown([])
        self.assertIn("| Task Name |", md)
        self.assertIn("Generated on Day 14", md)


if __name__ == "__main__":
    unittest.main()
