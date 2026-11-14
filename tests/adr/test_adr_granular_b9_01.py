"""Granular test 1: Section 19 in ADR-0098."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestAdrGranularB901(unittest.TestCase):
    def test_section_19_in_0098(self):
        p = list((REPO_ROOT / "docs" / "adr").glob("adr-0098-*.md"))[0]
        self.assertIn("Section 19", p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
