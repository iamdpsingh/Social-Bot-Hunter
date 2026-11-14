"""Granular test 3: db restore commands in 0103."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestRbGranularB803(unittest.TestCase):
    def test_db_restore_in_0103(self):
        p = list((REPO_ROOT / "docs" / "runbooks").glob("runbook-0103-*.md"))[0]
        text = p.read_text(encoding="utf-8")
        self.assertIn("db-verify", text)
        self.assertIn("db-restore", text)


if __name__ == "__main__":
    unittest.main()
