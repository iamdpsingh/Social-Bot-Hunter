"""Granular test 10: foreign key documentation."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestDocsGranularB710(unittest.TestCase):
    def test_foreign_keys_documented(self):
        path = REPO_ROOT / "docs" / "data-dictionary.md"
        text = path.read_text(encoding="utf-8")
        self.assertIn("FOREIGN KEY", text)


if __name__ == "__main__":
    unittest.main()
