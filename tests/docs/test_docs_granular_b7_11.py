"""Granular test 11: simhash_64 documentation."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestDocsGranularB711(unittest.TestCase):
    def test_simhash_column_documented(self):
        path = REPO_ROOT / "docs" / "data-dictionary.md"
        text = path.read_text(encoding="utf-8")
        self.assertIn("simhash_64", text)


if __name__ == "__main__":
    unittest.main()
