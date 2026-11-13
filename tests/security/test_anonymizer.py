"""Tests for deterministic pseudonymizer and attribute masking."""

from __future__ import annotations

import unittest

from sbh.security.anonymizer import (
    mask_ip_address,
    mask_phone_number,
    pseudonymize_identifier,
    sanitize_profile_attributes,
)


class TestAnonymizer(unittest.TestCase):
    def test_deterministic_pseudonym(self) -> None:
        p1 = pseudonymize_identifier("user_twitter_12345")
        p2 = pseudonymize_identifier("user_twitter_12345")
        p3 = pseudonymize_identifier("user_twitter_67890")
        self.assertEqual(p1, p2)
        self.assertNotEqual(p1, p3)
        self.assertTrue(p1.startswith("anon_"))

    def test_salt_influence(self) -> None:
        p1 = pseudonymize_identifier("test_user", salt="salt_a")
        p2 = pseudonymize_identifier("test_user", salt="salt_b")
        self.assertNotEqual(p1, p2)

    def test_mask_ip_address(self) -> None:
        self.assertEqual(mask_ip_address("192.168.1.42"), "192.168.0.0")

    def test_mask_phone_number(self) -> None:
        masked = mask_phone_number("+1-555-867-5309")
        self.assertTrue(masked.endswith("09"))
        self.assertNotIn("867", masked)

    def test_sanitize_profile_attributes(self) -> None:
        raw = {
            "username": "bot_hunter",
            "email": "hunter@internal.gov",
            "phone": "555-0199",
            "account_age_days": 450,
        }
        sanitized = sanitize_profile_attributes(raw)
        self.assertEqual(sanitized["email"], "[REDACTED_PRIVACY]")
        self.assertEqual(sanitized["phone"], "[REDACTED_PRIVACY]")
        self.assertEqual(sanitized["username"], "bot_hunter")
        self.assertEqual(sanitized["account_age_days"], 450)


if __name__ == "__main__":
    unittest.main()
