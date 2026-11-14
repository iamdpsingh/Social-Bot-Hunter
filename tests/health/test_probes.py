"""Tests for individual subsystem health probes."""

from __future__ import annotations

import unittest
from pathlib import Path

from sbh.health.probes import HealthProbeRunner, SubsystemStatus


class TestHealthProbes(unittest.TestCase):
    def test_sqlite_in_memory_probe(self):
        res = HealthProbeRunner.check_sqlite()
        self.assertEqual(res.status, SubsystemStatus.HEALTHY)
        self.assertEqual(res.subsystem, "database_sqlite")
        self.assertGreater(res.latency_ms, 0.0)

    def test_storage_directories_probe(self):
        temp_data = Path("data/temp_probe_test")
        res = HealthProbeRunner.check_storage_directories(temp_data)
        self.assertEqual(res.status, SubsystemStatus.HEALTHY)
        self.assertEqual(res.subsystem, "filesystem_storage")

    def test_model_artifacts_probe(self):
        res = HealthProbeRunner.check_model_artifacts()
        self.assertEqual(res.status, SubsystemStatus.HEALTHY)
        self.assertEqual(res.subsystem, "ml_model_artifacts")


if __name__ == "__main__":
    unittest.main()
