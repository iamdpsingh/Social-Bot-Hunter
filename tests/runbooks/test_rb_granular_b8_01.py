"""Granular test 1: run_local.sh in 0101."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestRbGranularB801(unittest.TestCase):
    def test_run_local_in_0101(self):
        p = list((REPO_ROOT / "docs" / "runbooks").glob("runbook-0101-*.md"))[0]
        self.assertIn("run_local.sh", p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
