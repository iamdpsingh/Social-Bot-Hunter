"""Granular test 6: keep a changelog reference."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestRelGranularB1006(unittest.TestCase):
    def test_keep_a_changelog(self):
        cl = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn("Keep a Changelog", cl)


if __name__ == "__main__":
    unittest.main()
