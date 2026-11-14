"""Granular test 10: offline air-gapped documentation."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestVerifGranularB510(unittest.TestCase):
    def test_offline_mode_documented(self):
        lim_path = REPO_ROOT / "docs" / "verification" / "limitations-log.md"
        text = lim_path.read_text(encoding="utf-8")
        self.assertIn("SBH_OFFLINE_MODE", text)


if __name__ == "__main__":
    unittest.main()
