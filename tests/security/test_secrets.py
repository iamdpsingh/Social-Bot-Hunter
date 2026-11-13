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
        aws_sample = "AK" + "IAIOSFODNN7EXAMPLE"
        self.assertEqual(mask_secret(aws_sample), "AKIA...MPLE")

    def test_scan_text_clean(self) -> None:
        findings = self.scanner.scan_text("def hello(): return 'world'")
        self.assertEqual(len(findings), 0)

    def test_scan_text_with_github_token(self) -> None:
        token = "gh" + "p_aB3dE5gH7iJ9kL1mN3oP5qR7sT9uV1wX3yZ5"
        sample = f"GITHUB_PAT={token}"
        findings = self.scanner.scan_text(sample)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule_id, "SEC-002")
        self.assertIn("...", findings[0].masked_value)

    def test_scan_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "creds.py"
            key = "s" + "k-abcdef1234567890abcdef123456789012"
            f.write_text(f"API_KEY = '{key}'")
            findings = self.scanner.scan_file(f)
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].rule_id, "SEC-007")

    def test_scan_directory_with_ignored_dir(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            (base / ".git").mkdir()
            token = "gh" + "p_aB3dE5gH7iJ9kL1mN3oP5qR7sT9uV1wX3yZ5"
            (base / ".git" / "config").write_text(token)
            (base / "src").mkdir()
            (base / "src" / "app.py").write_text("print('clean app')")
            findings = self.scanner.scan_directory(base)
            self.assertEqual(len(findings), 0)


if __name__ == "__main__":
    unittest.main()
