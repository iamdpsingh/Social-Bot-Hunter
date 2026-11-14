"""Granular test 4: benchmark report link."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestDocsGranularB704(unittest.TestCase):
    def test_benchmark_report_link_exists(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("docs/benchmarks/latency-report.md", readme)
        self.assertTrue((REPO_ROOT / "docs" / "benchmarks" / "latency-report.md").exists())


if __name__ == "__main__":
    unittest.main()
