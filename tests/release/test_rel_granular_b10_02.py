"""Granular test 2: status report 97."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestRelGranularB1002(unittest.TestCase):
    def test_report_97_exists(self):
        p = REPO_ROOT / "docs" / "status" / "day-14" / "97-day-14-e2e-and-benchmarks.md"
        self.assertTrue(p.exists())


if __name__ == "__main__":
    unittest.main()
