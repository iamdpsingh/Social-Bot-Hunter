"""Granular security CLI assertion suite 12 for isolated verification."""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout

from sbh.cli import main


class TestGranularSecCLIBatch7_12(unittest.TestCase):
    def test_cli_secrets_case_12(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = main(["audit-secrets", "--dir", td, "--json"])
            self.assertEqual(code, 0)
            self.assertIn('"total_findings": 0', buf.getvalue())


if __name__ == "__main__":
    unittest.main()
