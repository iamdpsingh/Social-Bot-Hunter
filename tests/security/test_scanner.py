"""Tests for SecurityAuditRunner and system configuration checks."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sbh.security.scanner import (
    SecurityAuditRunner,
    SecurityAuditSummary,
    check_debug_flags_in_environment,
    check_insecure_file_permissions,
)


class TestSecurityScannerCoordinator(unittest.TestCase):
    def test_check_debug_flags_clean(self) -> None:
        with patch.dict(os.environ, {"DEBUG": "", "SBH_DEBUG": ""}, clear=True):
            res = check_debug_flags_in_environment()
            self.assertTrue(res.passed)
            self.assertEqual(res.findings_count, 0)

    def test_check_debug_flags_violation(self) -> None:
        with patch.dict(os.environ, {"DEBUG": "true"}):
            res = check_debug_flags_in_environment()
            self.assertFalse(res.passed)
            self.assertIn("DEBUG", res.details["active_debug_flags"])

    def test_check_insecure_file_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            res = check_insecure_file_permissions(base)
            self.assertTrue(res.passed)

    def test_run_full_audit(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            runner = SecurityAuditRunner(base_dir=Path(td))
            with patch.dict(os.environ, {"DEBUG": ""}, clear=True):
                summary = runner.run_full_audit()
                self.assertIsInstance(summary, SecurityAuditSummary)
                self.assertTrue(summary.passed_audit)
                self.assertEqual(summary.failed_checks, 0)
                d = summary.to_dict()
                self.assertIn("passed_audit", d)


if __name__ == "__main__":
    unittest.main()
