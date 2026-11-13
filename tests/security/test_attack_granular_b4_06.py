"""Granular attack surface assertion suite 06 for isolated verification."""

from __future__ import annotations

import unittest

from sbh.shared.safety import csv_safe_cell


class TestGranularAttackBatch4_06(unittest.TestCase):
    def test_formula_variant_case_06(self) -> None:
        payload = f"=cmd_06|'test'!A0"
        self.assertTrue(csv_safe_cell(payload).startswith("'"))

    def test_clean_input_case_06(self) -> None:
        token = f"valid_identifier_06"
        self.assertEqual(csv_safe_cell(token), token)


if __name__ == "__main__":
    unittest.main()
