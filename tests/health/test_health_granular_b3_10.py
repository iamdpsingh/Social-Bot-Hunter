"""Granular test 10: free disk space metric."""

from __future__ import annotations

import unittest
from sbh.health.probes import HealthProbeRunner


class TestHealthGranularB310(unittest.TestCase):
    def test_free_gb_metric(self):
        res = HealthProbeRunner.check_storage_directories()
        self.assertIn("free_gb", res.metadata)
        self.assertGreater(res.metadata["free_gb"], 0.0)


if __name__ == "__main__":
    unittest.main()
