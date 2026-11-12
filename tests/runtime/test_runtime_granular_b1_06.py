"""Granular validation test 06 for local runtime environment."""

from __future__ import annotations

import unittest
from pathlib import Path
from sbh.runtime.sanitizer import SecretSanitizer
from sbh.runtime.system_info import collect_system_resources
from sbh.runtime.env_validator import is_port_in_use


class TestRuntimeGranularB106(unittest.TestCase):
    def test_granular_assertion_06(self) -> None:
        s = SecretSanitizer()
        self.assertTrue(s.is_key_sensitive("token_06"))
        snap = collect_system_resources()
        self.assertGreater(snap.uptime_seconds, -1)
        self.assertIsInstance(is_port_in_use(18000 + 6), bool)


if __name__ == "__main__":
    unittest.main()
