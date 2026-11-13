"""Granular privacy audit suite 14 for isolated verification."""

from __future__ import annotations

import unittest

from sbh.security.anonymizer import pseudonymize_identifier
from sbh.security.privacy import PIIType, PrivacyAuditor


class TestGranularPrivacyBatch2_14(unittest.TestCase):
    def test_pseudonym_length_case_14(self) -> None:
        anon = pseudonymize_identifier("id_case_14")
        self.assertEqual(len(anon), 21)  # 'anon_' (5) + 16 hex chars

    def test_auditor_empty_string_case_14(self) -> None:
        auditor = PrivacyAuditor()
        findings = auditor.audit_text("")
        self.assertEqual(len(findings), 0)

    def test_pii_type_values_case_14(self) -> None:
        self.assertEqual(PIIType.EMAIL.value, "EMAIL")
        self.assertEqual(PIIType.PHONE.value, "PHONE")
        self.assertEqual(PIIType.IPV4.value, "IPV4")


if __name__ == "__main__":
    unittest.main()
