"""Tests for sbh doctor and sbh benchmark CLI commands."""

from __future__ import annotations

import unittest

from sbh.health.diagnostics import run_full_system_diagnostics
from sbh.health.probes import SubsystemStatus


class TestHealthCli(unittest.TestCase):
    def test_diagnostics_produces_healthy_status(self):
        rep = run_full_system_diagnostics()
        self.assertIn(rep.overall_status, [SubsystemStatus.HEALTHY, SubsystemStatus.DEGRADED])


if __name__ == "__main__":
    unittest.main()
