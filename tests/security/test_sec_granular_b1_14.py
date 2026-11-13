"""Granular security audit suite 14 for isolated verification."""

from __future__ import annotations

import unittest

from sbh.security.patterns import calculate_shannon_entropy, get_default_rules
from sbh.security.secrets import SecretScanner, mask_secret


class TestGranularSecBatch1_14(unittest.TestCase):
    def test_shannon_entropy_case_14(self) -> None:
        token = "token_granular_14_abcXYZ123!#"
        entropy = calculate_shannon_entropy(token)
        self.assertGreater(entropy, 2.0)

    def test_mask_secret_case_14(self) -> None:
        secret = "secret_value_with_enough_length_for_mask_14"
        masked = mask_secret(secret, unmasked_chars=3)
        self.assertTrue(masked.startswith("sec..."))
        self.assertTrue(masked.endswith("_14"))

    def test_rules_uniqueness_14(self) -> None:
        rules = get_default_rules()
        ids = [r.rule_id for r in rules]
        self.assertEqual(len(ids), len(set(ids)))

    def test_scanner_instantiation_14(self) -> None:
        scanner = SecretScanner()
        self.assertIsNotNone(scanner)
        self.assertGreaterEqual(len(scanner.rules), 8)


if __name__ == "__main__":
    unittest.main()
