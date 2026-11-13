"""Granular attack surface assertion suite 04 for isolated verification."""

from __future__ import annotations

import unittest

from sbh.shared.safety import csv_safe_cell


class TestGranularAttackBatch4_04(unittest.TestCase):
    def test_formula_variant_case_04(self) -> None:
        payload = "=cmd_04|'test'!A0"
        self.assertTrue(csv_safe_cell(payload).startswith("'"))

    def test_clean_input_case_04(self) -> None:
        token = "valid_identifier_04"
        self.assertEqual(csv_safe_cell(token), token)


if __name__ == "__main__":
    unittest.main()
