"""Multi-platform verification testing Twitter, Bluesky, Mastodon, Reddit, YouTube."""

from __future__ import annotations

import unittest

from sbh.e2e.pipeline import E2EPipelineVerifier
from sbh.e2e.platforms import MultiPlatformMockGenerator


class TestE2EMultiPlatform(unittest.TestCase):
    """Test pipeline verification across all 5 supported platforms."""

    def test_all_five_platforms_produce_valid_graphs(self):
        for platform in MultiPlatformMockGenerator.SUPPORTED_PLATFORMS:
            with self.subTest(platform=platform):
                bots = MultiPlatformMockGenerator.generate_campaign_accounts(platform, campaign_size=3)
                human = MultiPlatformMockGenerator.generate_human_account(platform, f"real_{platform}_user")
                result = E2EPipelineVerifier.run_pipeline([*bots, human])

                self.assertTrue(result.success)
                self.assertEqual(result.total_accounts, 4)
                self.assertEqual(result.detected_bots, 3)
                self.assertTrue(result.cytoscape_report.is_valid)
                self.assertEqual(result.cytoscape_report.risk_distribution["bot"], 3)
                self.assertEqual(result.cytoscape_report.risk_distribution["human"], 1)


if __name__ == "__main__":
    unittest.main()
