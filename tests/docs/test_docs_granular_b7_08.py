"""Granular test 8: port numbers documented."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestDocsGranularB708(unittest.TestCase):
    def test_ports_documented(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(":3000", readme)
        self.assertIn(":8000", readme)


if __name__ == "__main__":
    unittest.main()
