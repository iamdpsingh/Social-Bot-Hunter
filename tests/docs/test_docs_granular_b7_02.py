"""Granular test 2: acceptance matrix link."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestDocsGranularB702(unittest.TestCase):
    def test_acceptance_matrix_link_exists(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("docs/verification/acceptance-matrix.md", readme)
        self.assertTrue((REPO_ROOT / "docs" / "verification" / "acceptance-matrix.md").exists())


if __name__ == "__main__":
    unittest.main()
