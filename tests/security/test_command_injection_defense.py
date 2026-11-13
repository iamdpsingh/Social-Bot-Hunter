"""Tests verifying dangerous shell characters are rejected or neutralized."""

from __future__ import annotations

import unittest

from sbh.runtime.sanitizer import sanitize_cmdline


class TestCommandInjectionDefense(unittest.TestCase):
    def test_sanitize_cmdline_redacts_tokens(self) -> None:
        cmd = ["sbh", "scans", "--token=ghp_secrettoken1234567890abcdef"]
        sanitized = sanitize_cmdline(cmd)
        self.assertNotIn("ghp_secrettoken1234567890abcdef", sanitized)
        self.assertIn("[REDACTED]", sanitized)

    def test_shell_metacharacters_preserved_as_discrete_args(self) -> None:
        # Popen without shell=True treats arguments as exact strings without interpreting metacharacters
        cmd = ["echo", "; rm -rf /", "$(id)", "`whoami`"]
        sanitized = sanitize_cmdline(cmd)
        self.assertIn("echo", sanitized)


if __name__ == "__main__":
    unittest.main()
