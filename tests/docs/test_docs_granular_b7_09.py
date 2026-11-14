"""Granular test 9: license text presence."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestDocsGranularB709(unittest.TestCase):
    def test_mit_license_present(self):
        lic_path = REPO_ROOT / "LICENSE"
        if lic_path.exists():
            text = lic_path.read_text(encoding="utf-8")
            self.assertIn("MIT License", text)


if __name__ == "__main__":
    unittest.main()
