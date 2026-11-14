"""Granular test 7: test matrix summary inspection."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestVerifGranularB507(unittest.TestCase):
    def test_test_matrix_summary_content(self):
        path = REPO_ROOT / "docs" / "verification" / "test-matrix-summary.md"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        self.assertIn("unittest", text)
        self.assertIn("pytest", text)
        self.assertIn("vitest", text)
        self.assertIn("100%", text)


if __name__ == "__main__":
    unittest.main()
