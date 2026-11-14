"""Tests for data dictionary schema documentation."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestDataDictionaryDoc(unittest.TestCase):
    def test_core_tables_documented(self):
        path = REPO_ROOT / "docs" / "data-dictionary.md"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        for table in ["scans", "platform_accounts", "account_observations", "coordination_campaigns"]:
            with self.subTest(table=table):
                self.assertIn(f"Table: `{table}`", text)


if __name__ == "__main__":
    unittest.main()
