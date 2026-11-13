"""Tests for SecretScanner with text, file, and directory scanning."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sbh.security.secrets import SecretScanner, mask_secret


class TestSecretScanner(unittest.TestCase):
    def setUp(self) -> None:
        self.scanner = SecretScanner()

    def test_mask_secret(self) -> None:
        self.assertEqual(mask_secret("short"), "[REDACTED]")
        self.assertEqual(mask_secret("AKIAIOSFODNN7EXAMPLE"), "AKIA...MPLE")

    def test_scan_text_clean(self) -> None:
        findings = self.scanner.scan_text("def hello(): return 'world'")
        self.assertEqual(len(findings), 0)

    def test_scan_text_with_github_token(self) -> None:
        sample = "GITHUB_PAT=ghp_aB3dE5gH7iJ9kL1mN3oP5qR7sT9uV1wX3yZ5"
        findings = self.scanner.scan_text(sample)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule_id, "SEC-002")
        self.assertIn("...", findings[0].masked_value)

    def test_scan_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "creds.py"
            f.write_text("API_KEY = 'sk-abcdef1234567890abcdef123456789012'")
            findings = self.scanner.scan_file(f)
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].rule_id, "SEC-007")

    def test_scan_directory_with_ignored_dir(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            (base / ".git").mkdir()
            (base / ".git" / "config").write_text("ghp_aB3dE5gH7iJ9kL1mN3oP5qR7sT9uV1wX3yZ5")
            (base / "src").mkdir()
            (base / "src" / "app.py").write_text("print('clean app')")
            findings = self.scanner.scan_directory(base)
            self.assertEqual(len(findings), 0)


if __name__ == "__main__":
    unittest.main()
