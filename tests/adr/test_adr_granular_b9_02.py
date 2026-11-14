"""Granular test 2: p99 SLA in ADR-0099."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestAdrGranularB902(unittest.TestCase):
    def test_p99_in_0099(self):
        p = list((REPO_ROOT / "docs" / "adr").glob("adr-0099-*.md"))[0]
        self.assertIn("p99", p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
