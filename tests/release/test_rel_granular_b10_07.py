"""Granular test 7: Day 14 completed mark."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestRelGranularB1007(unittest.TestCase):
    def test_day_14_completed_marker(self):
        plan = (REPO_ROOT / "docs" / "14-day-master-plan.md").read_text(encoding="utf-8")
        self.assertIn("Day 14 (14 Nov 2026): Production Acceptance, End-to-End Verification & Launch [COMPLETED]", plan)


if __name__ == "__main__":
    unittest.main()
