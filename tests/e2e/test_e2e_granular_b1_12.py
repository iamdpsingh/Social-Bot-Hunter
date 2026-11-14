"""Granular test 12 for edge id string formatting."""

from __future__ import annotations

import unittest
from sbh.e2e.pipeline import E2EPipelineVerifier
from sbh.e2e.platforms import MultiPlatformMockGenerator


class TestE2EGranularB112(unittest.TestCase):
    def test_edge_id_arrow_syntax(self):
        bots = MultiPlatformMockGenerator.generate_campaign_accounts("reddit", campaign_size=2)
        result = E2EPipelineVerifier.run_pipeline(bots)
        edge = result.cytoscape_elements["edges"][0]
        self.assertIn("->", edge["data"]["id"])


if __name__ == "__main__":
    unittest.main()
