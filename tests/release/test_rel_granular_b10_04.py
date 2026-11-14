"""Granular test 4: status report 99."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestRelGranularB1004(unittest.TestCase):
    def test_report_99_exists(self):
        p = REPO_ROOT / "docs" / "status" / "day-14" / "99-day-14-documentation-sweep.md"
        self.assertTrue(p.exists())


if __name__ == "__main__":
    unittest.main()
