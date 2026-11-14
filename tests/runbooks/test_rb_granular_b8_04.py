"""Granular test 4: sbh benchmark in 0104."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestRbGranularB804(unittest.TestCase):
    def test_sbh_benchmark_in_0104(self):
        p = list((REPO_ROOT / "docs" / "runbooks").glob("runbook-0104-*.md"))[0]
        self.assertIn("sbh benchmark", p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
