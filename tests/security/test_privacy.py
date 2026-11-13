"""Tests for PrivacyAuditor and PII detection patterns."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sbh.security.privacy import PIIType, PrivacyAuditor, mask_pii


class TestPrivacyAuditor(unittest.TestCase):
    def setUp(self) -> None:
        self.auditor = PrivacyAuditor()

    def test_mask_pii_email(self) -> None:
        masked = mask_pii("investigator@example.com", PIIType.EMAIL)
        self.assertEqual(masked, "i***@example.com")

    def test_audit_text_with_email_and_phone(self) -> None:
        text = "Contact me at alice@testcorp.com or 555-123-4567 for info."
        findings = self.auditor.audit_text(text)
        self.assertEqual(len(findings), 2)
        types = {f.pii_type for f in findings}
        self.assertIn(PIIType.EMAIL, types)
        self.assertIn(PIIType.PHONE, types)

    def test_audit_directory_clean(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            (base / "export.json").write_text('{"user_id": "anon_12345", "score": 0.85}')
            report = self.auditor.audit_directory(base)
            self.assertTrue(report.passed)
            self.assertEqual(report.total_findings, 0)
            self.assertEqual(report.scanned_sources, 1)

    def test_audit_directory_violation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            (base / "leak.csv").write_text("id,email\n1,user@target.org")
            report = self.auditor.audit_directory(base)
            self.assertFalse(report.passed)
            self.assertEqual(report.total_findings, 1)


if __name__ == "__main__":
    unittest.main()
