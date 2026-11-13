"""Tests verifying spreadsheet formulas are prefixed with single quote in export cells."""

from __future__ import annotations

import unittest

from sbh.shared.safety import csv_safe_cell


class TestCsvFormulaInjectionDefense(unittest.TestCase):
    def test_formula_prefixes(self) -> None:
        payloads = [
            "=1+1",
            "@SUM(A1:A10)",
            "-CMD|' /C calc'!A0",
            "+1234567890",
            "	=calc",
            "=calc",
        ]
        for p in payloads:
            safe = csv_safe_cell(p)
            self.assertTrue(safe.startswith("'"), f"Payload {p!r} was not properly quoted: {safe!r}")

    def test_safe_cells_unchanged(self) -> None:
        self.assertEqual(csv_safe_cell("normal_username"), "normal_username")
        self.assertEqual(csv_safe_cell("42"), "42")


if __name__ == "__main__":
    unittest.main()
