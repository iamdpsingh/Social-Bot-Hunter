"""Tests for pattern detection rules and Shannon entropy calculator."""

from __future__ import annotations

import unittest

from sbh.security.patterns import (
    RuleSeverity,
    calculate_shannon_entropy,
    get_default_rules,
)


class TestSecurityPatterns(unittest.TestCase):
    def test_calculate_shannon_entropy_empty(self) -> None:
        self.assertEqual(calculate_shannon_entropy(""), 0.0)

    def test_calculate_shannon_entropy_uniform(self) -> None:
        self.assertEqual(calculate_shannon_entropy("aaaa"), 0.0)

    def test_calculate_shannon_entropy_high_diversity(self) -> None:
        entropy = calculate_shannon_entropy("aB3$9zK!pQ8#vL1@")
        self.assertGreater(entropy, 3.5)

    def test_default_rules_presence(self) -> None:
        rules = get_default_rules()
        self.assertGreaterEqual(len(rules), 8)
        ids = [r.rule_id for r in rules]
        self.assertIn("SEC-001", ids)
        self.assertIn("SEC-002", ids)
        self.assertIn("SEC-005", ids)

    def test_aws_pattern_detection(self) -> None:
        rules = {r.rule_id: r for r in get_default_rules()}
        aws_rule = rules["SEC-001"]
        self.assertEqual(aws_rule.severity, RuleSeverity.CRITICAL)
        sample = "AK" + "IAIOSFODNN7EXAMPLE"
        match = aws_rule.regex.search(sample)
        self.assertIsNotNone(match)
        if match:
            self.assertEqual(match.group(1), sample)

    def test_github_pat_detection(self) -> None:
        rules = {r.rule_id: r for r in get_default_rules()}
        gh_rule = rules["SEC-002"]
        token = "gh" + "p_1234567890abcdefghijklmnopqrstuvwxyz"
        match = gh_rule.regex.search(f"export GITHUB_TOKEN={token}")
        self.assertIsNotNone(match)


if __name__ == "__main__":
    unittest.main()
