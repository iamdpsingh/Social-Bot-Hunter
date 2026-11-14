"""Tests verifying Day 14 runbooks."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestRunbookSuite(unittest.TestCase):
    def test_runbooks_101_to_110_exist_and_have_required_sections(self):
        runbooks_dir = REPO_ROOT / "docs" / "runbooks"
        for i in range(101, 111):
            matches = list(runbooks_dir.glob(f"runbook-0{i}-*.md"))
            self.assertEqual(len(matches), 1, f"RUNBOOK-0{i} must exist")
            text = matches[0].read_text(encoding="utf-8")
            self.assertIn("## Scope & Target", text)
            self.assertTrue(len(text) > 100)


if __name__ == "__main__":
    unittest.main()
