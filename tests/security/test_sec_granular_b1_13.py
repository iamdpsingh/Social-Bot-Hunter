"""Granular security audit suite 13 for isolated verification."""

from __future__ import annotations

import unittest
from sbh.security.patterns import calculate_shannon_entropy, get_default_rules
from sbh.security.secrets import SecretScanner, mask_secret


class TestGranularSecBatch1_13(unittest.TestCase):
    def test_shannon_entropy_case_13(self) -> None:
        token = "token_granular_13_abcXYZ123!#"
        entropy = calculate_shannon_entropy(token)
        self.assertGreater(entropy, 2.0)

    def test_mask_secret_case_13(self) -> None:
        secret = "secret_value_with_enough_length_for_mask_13"
        masked = mask_secret(secret, unmasked_chars=3)
        self.assertTrue(masked.startswith("sec..."))
        self.assertTrue(masked.endswith("_13"))

    def test_rules_uniqueness_13(self) -> None:
        rules = get_default_rules()
        ids = [r.rule_id for r in rules]
        self.assertEqual(len(ids), len(set(ids)))

    def test_scanner_instantiation_13(self) -> None:
        scanner = SecretScanner()
        self.assertIsNotNone(scanner)
        self.assertGreaterEqual(len(scanner.rules), 8)


if __name__ == "__main__":
    unittest.main()
