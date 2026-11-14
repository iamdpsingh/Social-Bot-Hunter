"""Granular test 1: master plan link."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestDocsGranularB701(unittest.TestCase):
    def test_master_plan_link_exists(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("docs/14-day-master-plan.md", readme)
        self.assertTrue((REPO_ROOT / "docs" / "14-day-master-plan.md").exists())


if __name__ == "__main__":
    unittest.main()
