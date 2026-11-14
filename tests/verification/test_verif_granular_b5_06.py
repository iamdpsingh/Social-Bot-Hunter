"""Granular test 6: limitations log inspection."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestVerifGranularB506(unittest.TestCase):
    def test_limitations_file_mentions_platforms(self):
        lim_path = REPO_ROOT / "docs" / "verification" / "limitations-log.md"
        self.assertTrue(lim_path.exists())
        text = lim_path.read_text(encoding="utf-8")
        self.assertIn("Twitter/X", text)
        self.assertIn("Bluesky", text)
        self.assertIn("Mastodon", text)
        self.assertIn("Reddit", text)
        self.assertIn("YouTube", text)


if __name__ == "__main__":
    unittest.main()
