"""Granular test 2: sbh doctor in 0102."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestRbGranularB802(unittest.TestCase):
    def test_sbh_doctor_in_0102(self):
        p = list((REPO_ROOT / "docs" / "runbooks").glob("runbook-0102-*.md"))[0]
        self.assertIn("sbh doctor", p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
