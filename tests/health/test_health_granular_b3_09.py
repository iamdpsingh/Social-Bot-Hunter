"""Granular test 9: temporary record insertion."""

from __future__ import annotations

import unittest
from sbh.health.probes import HealthProbeRunner


class TestHealthGranularB309(unittest.TestCase):
    def test_sqlite_in_memory_temporary_write(self):
        res = HealthProbeRunner.check_sqlite(":memory:")
        self.assertEqual(res.metadata["rows"], 1)


if __name__ == "__main__":
    unittest.main()
