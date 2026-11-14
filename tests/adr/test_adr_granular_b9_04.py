"""Granular test 4: sbh doctor in ADR-0101."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestAdrGranularB904(unittest.TestCase):
    def test_doctor_in_0101(self):
        p = list((REPO_ROOT / "docs" / "adr").glob("adr-0101-*.md"))[0]
        self.assertIn("sbh doctor", p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
