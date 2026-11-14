"""Granular test 8: v1.0.0 in 0110."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestRbGranularB808(unittest.TestCase):
    def test_v1_release_in_0110(self):
        p = list((REPO_ROOT / "docs" / "runbooks").glob("runbook-0110-*.md"))[0]
        self.assertIn("v1.0.0", p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
