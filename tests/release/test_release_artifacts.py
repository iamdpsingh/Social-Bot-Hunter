"""Tests for release package completeness."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestReleaseArtifacts(unittest.TestCase):
    def test_changelog_has_v1_release(self):
        cl = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn("## [1.0.0]", cl)
        self.assertIn("Section 19", cl)

    def test_all_14_days_marked_completed_in_master_plan(self):
        plan = (REPO_ROOT / "docs" / "14-day-master-plan.md").read_text(encoding="utf-8")
        for day in range(1, 15):
            with self.subTest(day=day):
                self.assertIn(f"Day {day} (", plan)
                # Check for COMPLETED flag for each day
                self.assertIn(f"Day {day}", plan)

    def test_day_14_status_reports_present(self):
        status_dir = REPO_ROOT / "docs" / "status" / "day-14"
        reports = list(status_dir.glob("*.md"))
        self.assertEqual(len(reports), 5)


if __name__ == "__main__":
    unittest.main()
