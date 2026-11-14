"""Granular test 6: markdown table rows."""

from __future__ import annotations

import unittest
from sbh.health.diagnostics import format_report_markdown, run_full_system_diagnostics


class TestHealthGranularB306(unittest.TestCase):
    def test_markdown_contains_table_pipes(self):
        rep = run_full_system_diagnostics()
        md = format_report_markdown(rep)
        self.assertIn("| `database_sqlite` |", md)


if __name__ == "__main__":
    unittest.main()
