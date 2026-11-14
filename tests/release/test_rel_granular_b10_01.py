"""Granular test 1: status report 96."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestRelGranularB1001(unittest.TestCase):
    def test_report_96_exists(self):
        p = REPO_ROOT / "docs" / "status" / "day-14" / "96-day-14-kickoff.md"
        self.assertTrue(p.exists())


if __name__ == "__main__":
    unittest.main()
