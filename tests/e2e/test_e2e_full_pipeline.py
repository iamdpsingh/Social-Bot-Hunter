"""Comprehensive end-to-end verification test for full analysis pipeline."""

from __future__ import annotations

import unittest

from sbh.e2e.pipeline import E2EPipelineVerifier
from sbh.e2e.platforms import MultiPlatformMockGenerator


class TestE2EFullPipeline(unittest.TestCase):
    """Test full pipeline execution from account ingestion to Cytoscape export."""

    def test_pipeline_with_coordinated_campaign_and_human(self):
        campaign = MultiPlatformMockGenerator.generate_campaign_accounts("twitter", campaign_size=5)
        human = MultiPlatformMockGenerator.generate_human_account("twitter", "alice_engineer")
        all_accounts = [*campaign, human]

        result = E2EPipelineVerifier.run_pipeline(all_accounts)

        self.assertTrue(result.success)
        self.assertEqual(result.total_accounts, 6)
        self.assertEqual(result.detected_bots, 5)
        self.assertEqual(result.coordinated_campaigns, 1)

        report = result.cytoscape_report
        self.assertTrue(report.is_valid)
        self.assertEqual(report.node_count, 6)
        # 5 members clique: 5 * 4 / 2 = 10 edges
        self.assertEqual(report.edge_count, 10)
        self.assertEqual(len(report.orphan_edges), 0)
        self.assertEqual(report.risk_distribution["bot"], 5)
        self.assertEqual(report.risk_distribution["human"], 1)

    def test_pipeline_empty_account_list(self):
        result = E2EPipelineVerifier.run_pipeline([])
        self.assertTrue(result.success)
        self.assertEqual(result.total_accounts, 0)
        self.assertEqual(result.cytoscape_report.node_count, 0)
        self.assertEqual(result.cytoscape_report.edge_count, 0)


if __name__ == "__main__":
    unittest.main()
