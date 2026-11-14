"""Granular test 5 for edge attributes."""

from __future__ import annotations

import unittest
from sbh.e2e.pipeline import E2EPipelineVerifier
from sbh.e2e.platforms import MultiPlatformMockGenerator


class TestE2EGranularB105(unittest.TestCase):
    def test_edge_data_has_relationship_type(self):
        bots = MultiPlatformMockGenerator.generate_campaign_accounts("youtube", campaign_size=2)
        result = E2EPipelineVerifier.run_pipeline(bots)
        edge_data = result.cytoscape_elements["edges"][0]["data"]
        self.assertIn("relationship_type", edge_data)
        self.assertIn("source", edge_data)
        self.assertIn("target", edge_data)


if __name__ == "__main__":
    unittest.main()
