"""Granular test 3: status report 98."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestRelGranularB1003(unittest.TestCase):
    def test_report_98_exists(self):
        p = REPO_ROOT / "docs" / "status" / "day-14" / "98-day-14-acceptance-matrix.md"
        self.assertTrue(p.exists())


if __name__ == "__main__":
    unittest.main()
