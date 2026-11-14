"""Granular test 7: run_local.sh documentation."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestDocsGranularB707(unittest.TestCase):
    def test_run_local_documented(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("./scripts/run_local.sh", readme)


if __name__ == "__main__":
    unittest.main()
