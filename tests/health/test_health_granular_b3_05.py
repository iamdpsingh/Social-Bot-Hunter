"""Granular test 5: model artifact metadata."""

from __future__ import annotations

import unittest
from sbh.health.probes import HealthProbeRunner


class TestHealthGranularB305(unittest.TestCase):
    def test_model_artifact_metadata(self):
        res = HealthProbeRunner.check_model_artifacts()
        self.assertIn("artifacts_count", res.metadata)


if __name__ == "__main__":
    unittest.main()
