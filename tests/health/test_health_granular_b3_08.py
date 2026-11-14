"""Granular test 8: ISO timestamp validation."""

from __future__ import annotations

import unittest
from datetime import datetime

from sbh.health.diagnostics import run_full_system_diagnostics


class TestHealthGranularB308(unittest.TestCase):
    def test_timestamp_iso_parse(self):
        rep = run_full_system_diagnostics()
        # Should parse without exception
        dt = datetime.fromisoformat(rep.timestamp)
        self.assertIsNotNone(dt)


if __name__ == "__main__":
    unittest.main()
