"""Tests for SecretSanitizer and command line redaction."""

from __future__ import annotations

import unittest

from sbh.runtime.sanitizer import (
    SecretSanitizer,
    format_safe_env,
    sanitize_cmdline,
    sanitize_mapping,
)


class TestSecretSanitizer(unittest.TestCase):
    def setUp(self) -> None:
        self.sanitizer = SecretSanitizer()

    def test_redact_sensitive_keys(self) -> None:
        data = {
            "api_key": "sk-1234567890abcdef",
            "password": "supersecretpassword",
            "user_token": "token_xyz",
            "safe_field": "hello world",
            "account_id": "acc-999",
        }
        res = self.sanitizer.sanitize_mapping(data)
        self.assertEqual(res["api_key"], "[REDACTED]")
        self.assertEqual(res["password"], "[REDACTED]")
        self.assertEqual(res["user_token"], "[REDACTED]")
        self.assertEqual(res["safe_field"], "hello world")
        self.assertEqual(res["account_id"], "acc-999")

    def test_nested_dictionary_redaction(self) -> None:
        nested = {
            "service": "postgres",
            "credentials": {
                "admin_password": "p@ssword!",
                "port": 5432,
            },
            "subsystems": [
                {"name": "worker", "auth_bearer": "Bearer token123"},
                {"name": "api", "status": "active"},
            ],
        }
        res = sanitize_mapping(nested)
        self.assertEqual(res["credentials"]["admin_password"], "[REDACTED]")
        self.assertEqual(res["credentials"]["port"], 5432)
        self.assertEqual(res["subsystems"][0]["auth_bearer"], "[REDACTED]")
        self.assertEqual(res["subsystems"][1]["status"], "active")

    def test_cmdline_redaction(self) -> None:
        argv = [
            "python",
            "app.py",
            "--db-password=supersecret",
            "--token",
            "secret_token_123",
            "--host",
            "127.0.0.1",
        ]
        redacted = sanitize_cmdline(argv)
        self.assertEqual(redacted[0], "python")
        self.assertEqual(redacted[1], "app.py")
        self.assertEqual(redacted[2], "--db-password=[REDACTED]")
        self.assertEqual(redacted[3], "--token")
        self.assertEqual(redacted[4], "[REDACTED]")
        self.assertEqual(redacted[5], "--host")
        self.assertEqual(redacted[6], "127.0.0.1")

    def test_bearer_string_redaction(self) -> None:
        raw = "Header Authorization: Bearer abc123def456-token"
        res = self.sanitizer.sanitize_string(raw)
        self.assertIn("Bearer [REDACTED]", res)
        self.assertNotIn("abc123def456-token", res)

    def test_format_safe_env(self) -> None:
        env = {
            "SBH_SECRET_KEY": "supersecretkey",
            "SBH_DATABASE_URL": "postgresql://usr:pass@localhost/db",
            "PATH": "/usr/bin:/bin",
            "PORT": "8000",
        }
        safe = format_safe_env(env)
        self.assertEqual(safe["SBH_SECRET_KEY"], "[REDACTED]")
        self.assertEqual(safe["SBH_DATABASE_URL"], "[REDACTED]")
        self.assertEqual(safe["PATH"], "/usr/bin:/bin")
        self.assertEqual(safe["PORT"], "8000")


if __name__ == "__main__":
    unittest.main()
