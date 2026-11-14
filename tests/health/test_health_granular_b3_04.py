"""Granular test 4: invalid directory handling."""

from __future__ import annotations

import unittest
from pathlib import Path
from sbh.health.probes import HealthProbeRunner, SubsystemStatus


class TestHealthGranularB304(unittest.TestCase):
    def test_nonexistent_read_only_path(self):
        res = HealthProbeRunner.check_storage_directories(Path("/dev/null/forbidden_path"))
        self.assertIn(res.status, [SubsystemStatus.DEGRADED, SubsystemStatus.UNHEALTHY])


if __name__ == "__main__":
    unittest.main()
