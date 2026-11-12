"""Granular validation test 02 for local runtime environment."""

from __future__ import annotations

import unittest
from pathlib import Path
from sbh.runtime.sanitizer import SecretSanitizer
from sbh.runtime.system_info import collect_system_resources
from sbh.runtime.env_validator import is_port_in_use


class TestRuntimeGranularB102(unittest.TestCase):
    def test_granular_assertion_02(self) -> None:
        s = SecretSanitizer()
        self.assertTrue(s.is_key_sensitive("token_02"))
        snap = collect_system_resources()
        self.assertGreater(snap.uptime_seconds, -1)
        self.assertIsInstance(is_port_in_use(18000 + 2), bool)


if __name__ == "__main__":
    unittest.main()
