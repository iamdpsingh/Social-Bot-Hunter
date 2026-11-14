"""Granular test 2 for dense clique networks."""

from __future__ import annotations

import unittest

from sbh.e2e.pipeline import E2EPipelineVerifier
from sbh.e2e.platforms import MultiPlatformMockGenerator


class TestE2EGranularB102(unittest.TestCase):
    def test_dense_clique_edge_count(self):
        n = 6
        bots = MultiPlatformMockGenerator.generate_campaign_accounts("bluesky", campaign_size=n)
        result = E2EPipelineVerifier.run_pipeline(bots)
        expected_edges = n * (n - 1) // 2
        self.assertEqual(result.cytoscape_report.edge_count, expected_edges)


if __name__ == "__main__":
    unittest.main()
