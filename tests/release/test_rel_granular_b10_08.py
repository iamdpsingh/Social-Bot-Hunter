"""Granular test 8: total status report count."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestRelGranularB1008(unittest.TestCase):
    def test_total_reports_is_at_least_100(self):
        status_root = REPO_ROOT / "docs" / "status"
        all_mds = list(status_root.glob("**/*.md"))
        self.assertGreaterEqual(len(all_mds), 100)


if __name__ == "__main__":
    unittest.main()
