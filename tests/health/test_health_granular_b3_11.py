"""Granular test 11: enum string compatibility."""

from __future__ import annotations

import unittest

from sbh.health.probes import SubsystemStatus


class TestHealthGranularB311(unittest.TestCase):
    def test_enum_is_str(self):
        self.assertEqual(str(SubsystemStatus.HEALTHY), "HEALTHY")
        self.assertEqual(f"{SubsystemStatus.DEGRADED}", "DEGRADED")


if __name__ == "__main__":
    unittest.main()
