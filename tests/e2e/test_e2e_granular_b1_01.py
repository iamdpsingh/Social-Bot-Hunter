"""Granular test 1 for empty and zero-edge networks."""

from __future__ import annotations

import unittest

from sbh.e2e.pipeline import E2EPipelineVerifier
from sbh.e2e.platforms import PlatformSampleAccount


class TestE2EGranularB101(unittest.TestCase):
    def test_isolated_singletons_have_zero_edges(self):
        acc1 = PlatformSampleAccount("twitter", "u1", "user1", "User 1", 10, 10, 5, "2024-01-01", "", False)
        acc2 = PlatformSampleAccount("twitter", "u2", "user2", "User 2", 20, 20, 8, "2024-01-01", "", False)
        result = E2EPipelineVerifier.run_pipeline([acc1, acc2])
        self.assertTrue(result.success)
        self.assertEqual(result.cytoscape_report.node_count, 2)
        self.assertEqual(result.cytoscape_report.edge_count, 0)


if __name__ == "__main__":
    unittest.main()
