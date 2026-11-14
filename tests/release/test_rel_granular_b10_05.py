"""Granular test 5: status report 100."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestRelGranularB1005(unittest.TestCase):
    def test_report_100_exists(self):
        p = REPO_ROOT / "docs" / "status" / "day-14" / "100-day-14-final-handover.md"
        self.assertTrue(p.exists())


if __name__ == "__main__":
    unittest.main()
