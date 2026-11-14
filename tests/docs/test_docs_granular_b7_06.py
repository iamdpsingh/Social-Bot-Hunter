"""Granular test 6: license file."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestDocsGranularB706(unittest.TestCase):
    def test_license_referenced(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("LICENSE", readme)


if __name__ == "__main__":
    unittest.main()
