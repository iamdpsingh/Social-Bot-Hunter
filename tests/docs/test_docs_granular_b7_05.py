"""Granular test 5: test matrix summary link."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestDocsGranularB705(unittest.TestCase):
    def test_test_matrix_summary_link_exists(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("docs/verification/test-matrix-summary.md", readme)
        self.assertTrue((REPO_ROOT / "docs" / "verification" / "test-matrix-summary.md").exists())


if __name__ == "__main__":
    unittest.main()
