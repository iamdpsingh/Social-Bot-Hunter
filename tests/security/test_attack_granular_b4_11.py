"""Granular attack surface assertion suite 11 for isolated verification."""

from __future__ import annotations

import unittest

from sbh.shared.safety import csv_safe_cell


class TestGranularAttackBatch4_11(unittest.TestCase):
    def test_formula_variant_case_11(self) -> None:
        payload = "=cmd_11|'test'!A0"
        self.assertTrue(csv_safe_cell(payload).startswith("'"))

    def test_clean_input_case_11(self) -> None:
        token = "valid_identifier_11"
        self.assertEqual(csv_safe_cell(token), token)


if __name__ == "__main__":
    unittest.main()
