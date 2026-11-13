"""Granular attack surface assertion suite 12 for isolated verification."""

from __future__ import annotations

import unittest

from sbh.shared.safety import csv_safe_cell


class TestGranularAttackBatch4_12(unittest.TestCase):
    def test_formula_variant_case_12(self) -> None:
        payload = f"=cmd_12|'test'!A0"
        self.assertTrue(csv_safe_cell(payload).startswith("'"))

    def test_clean_input_case_12(self) -> None:
        token = f"valid_identifier_12"
        self.assertEqual(csv_safe_cell(token), token)


if __name__ == "__main__":
    unittest.main()
