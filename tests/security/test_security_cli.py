"""Tests for security audit CLI subcommands."""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout

from sbh.cli import main


class TestSecurityCLI(unittest.TestCase):
    def test_audit_secrets_cli_clean(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = main(["audit-secrets", "--dir", td, "--json"])
            self.assertEqual(code, 0)
            self.assertIn('"passed": true', buf.getvalue())

    def test_audit_privacy_cli_clean(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = main(["audit-privacy", "--dir", td, "--json"])
            self.assertEqual(code, 0)
            self.assertIn('"passed": true', buf.getvalue())

    def test_audit_dependencies_cli(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(["audit-dependencies", "--json"])
        self.assertIn(code, {0, 1})
        self.assertIn('"python"', buf.getvalue())

    def test_audit_full_cli(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = main(["audit-full", "--dir", td, "--json"])
            self.assertEqual(code, 0)
            self.assertIn('"passed_audit": true', buf.getvalue())


if __name__ == "__main__":
    unittest.main()
