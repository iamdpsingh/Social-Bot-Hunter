"""Tests verifying Day 14 ADRs."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestAdrSuite(unittest.TestCase):
    def test_adrs_098_to_107_exist_and_have_required_sections(self):
        adr_dir = REPO_ROOT / "docs" / "adr"
        for i in range(98, 108):
            matches = list(adr_dir.glob(f"adr-0{i:03d}-*.md"))
            self.assertEqual(len(matches), 1, f"ADR-0{i:03d} must exist")
            text = matches[0].read_text(encoding="utf-8")
            self.assertIn("## Status", text)
            self.assertIn("Accepted", text)
            self.assertIn("## Context", text)
            self.assertIn("## Decision", text)
            self.assertIn("## Consequences", text)


if __name__ == "__main__":
    unittest.main()
