"""Granular test 6 for multi-campaign cluster isolation."""

from __future__ import annotations

import unittest
from sbh.e2e.pipeline import E2EPipelineVerifier
from sbh.e2e.platforms import MultiPlatformMockGenerator


class TestE2EGranularB106(unittest.TestCase):
    def test_multiple_distinct_campaigns(self):
        camp1 = MultiPlatformMockGenerator.generate_campaign_accounts("twitter", campaign_size=3, target_topic="crypto")
        camp2 = MultiPlatformMockGenerator.generate_campaign_accounts("twitter", campaign_size=3, target_topic="politics")
        result = E2EPipelineVerifier.run_pipeline([*camp1, *camp2])
        self.assertEqual(result.coordinated_campaigns, 2)
        self.assertEqual(len(result.cytoscape_report.cluster_counts), 2)


if __name__ == "__main__":
    unittest.main()
