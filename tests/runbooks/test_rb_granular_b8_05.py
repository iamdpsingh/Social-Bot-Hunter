"""Granular test 5: 5000 node ceiling in 0105."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestRbGranularB805(unittest.TestCase):
    def test_node_ceiling_in_0105(self):
        p = list((REPO_ROOT / "docs" / "runbooks").glob("runbook-0105-*.md"))[0]
        self.assertIn("5,000 nodes", p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
