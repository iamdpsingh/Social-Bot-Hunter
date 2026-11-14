"""Granular test 5: local venv in ADR-0102."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestAdrGranularB905(unittest.TestCase):
    def test_local_venv_in_0102(self):
        p = list((REPO_ROOT / "docs" / "adr").glob("adr-0102-*.md"))[0]
        self.assertIn(".venv", p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
