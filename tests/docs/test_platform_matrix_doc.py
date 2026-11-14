"""Tests for platform access matrix documentation."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestPlatformMatrixDoc(unittest.TestCase):
    def test_all_platforms_covered(self):
        path = REPO_ROOT / "docs" / "platform-access-matrix.md"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        for p in ["Twitter / X", "Bluesky", "Mastodon", "Reddit", "YouTube"]:
            with self.subTest(platform=p):
                self.assertIn(p, text)


if __name__ == "__main__":
    unittest.main()
