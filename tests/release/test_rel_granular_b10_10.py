"""Granular test 10: report 100 author attribution."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestRelGranularB1010(unittest.TestCase):
    def test_report_100_author(self):
        p = REPO_ROOT / "docs" / "status" / "day-14" / "100-day-14-final-handover.md"
        text = p.read_text(encoding="utf-8")
        self.assertIn("dpsingh <dhruvpratapsingh30.official2.o@gmail.com>", text)


if __name__ == "__main__":
    unittest.main()
