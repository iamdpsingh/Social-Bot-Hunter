"""Granular test 6: offline mode flag in 0106."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestRbGranularB806(unittest.TestCase):
    def test_offline_mode_in_0106(self):
        p = list((REPO_ROOT / "docs" / "runbooks").glob("runbook-0106-*.md"))[0]
        self.assertIn("SBH_OFFLINE_MODE", p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
