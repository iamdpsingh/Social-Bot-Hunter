"""Granular validation test 13 for local runtime environment."""

from __future__ import annotations

import unittest

from sbh.runtime.env_validator import is_port_in_use
from sbh.runtime.sanitizer import SecretSanitizer
from sbh.runtime.system_info import collect_system_resources


class TestRuntimeGranularB113(unittest.TestCase):
    def test_granular_assertion_13(self) -> None:
        s = SecretSanitizer()
        self.assertTrue(s.is_key_sensitive("token_13"))
        snap = collect_system_resources()
        self.assertGreater(snap.uptime_seconds, -1)
        self.assertIsInstance(is_port_in_use(18000 + 13), bool)


if __name__ == "__main__":
    unittest.main()
