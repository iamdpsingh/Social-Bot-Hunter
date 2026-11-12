"""Tests for CLI runtime commands."""

from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout

from sbh.cli import main


class TestRuntimeCLI(unittest.TestCase):
    def test_runtime_check_env_cli(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(["runtime-check-env", "--no-ports", "--json"])
        self.assertEqual(code, 0)
        self.assertIn('"all_passed": true', buf.getvalue())

    def test_runtime_status_cli(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(["runtime-status", "--json"])
        self.assertEqual(code, 0)
        self.assertIn('"services"', buf.getvalue())


if __name__ == "__main__":
    unittest.main()
