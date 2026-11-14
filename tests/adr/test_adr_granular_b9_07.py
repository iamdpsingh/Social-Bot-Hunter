"""Granular test 7: v1.0.0 tag in ADR-0106."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestAdrGranularB907(unittest.TestCase):
    def test_tag_in_0106(self):
        p = list((REPO_ROOT / "docs" / "adr").glob("adr-0106-*.md"))[0]
        self.assertIn("v1.0.0", p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
