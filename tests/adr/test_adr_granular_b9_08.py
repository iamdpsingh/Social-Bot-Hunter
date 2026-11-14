"""Granular test 8: master plan completion in ADR-0107."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestAdrGranularB908(unittest.TestCase):
    def test_completion_in_0107(self):
        p = list((REPO_ROOT / "docs" / "adr").glob("adr-0107-*.md"))[0]
        self.assertIn("14-Day Master Plan", p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
