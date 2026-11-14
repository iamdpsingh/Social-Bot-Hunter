"""Granular test 11: Cytoscape ceiling documentation."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestVerifGranularB511(unittest.TestCase):
    def test_node_ceiling_documented(self):
        lim_path = REPO_ROOT / "docs" / "verification" / "limitations-log.md"
        text = lim_path.read_text(encoding="utf-8")
        self.assertIn("5,000 nodes", text)


if __name__ == "__main__":
    unittest.main()
