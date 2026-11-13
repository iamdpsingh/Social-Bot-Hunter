"""Granular attack surface assertion suite 13 for isolated verification."""

from __future__ import annotations

import unittest

from sbh.shared.safety import csv_safe_cell


class TestGranularAttackBatch4_13(unittest.TestCase):
    def test_formula_variant_case_13(self) -> None:
        payload = "=cmd_13|'test'!A0"
        self.assertTrue(csv_safe_cell(payload).startswith("'"))

    def test_clean_input_case_13(self) -> None:
        token = "valid_identifier_13"
        self.assertEqual(csv_safe_cell(token), token)


if __name__ == "__main__":
    unittest.main()
