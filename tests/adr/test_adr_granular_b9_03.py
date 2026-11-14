"""Granular test 3: CytoscapeValidator in ADR-0100."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestAdrGranularB903(unittest.TestCase):
    def test_validator_in_0100(self):
        p = list((REPO_ROOT / "docs" / "adr").glob("adr-0100-*.md"))[0]
        self.assertIn("CytoscapeValidator", p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
