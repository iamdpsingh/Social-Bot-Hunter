"""Granular test 3: limitations log link."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestDocsGranularB703(unittest.TestCase):
    def test_limitations_log_link_exists(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("docs/verification/limitations-log.md", readme)
        self.assertTrue((REPO_ROOT / "docs" / "verification" / "limitations-log.md").exists())


if __name__ == "__main__":
    unittest.main()
