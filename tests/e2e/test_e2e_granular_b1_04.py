"""Granular test 4 for risk category thresholds."""

from __future__ import annotations

import unittest
from sbh.e2e.pipeline import E2EPipelineVerifier
from sbh.e2e.platforms import PlatformSampleAccount


class TestE2EGranularB104(unittest.TestCase):
    def test_risk_distribution_thresholds(self):
        bot = PlatformSampleAccount("reddit", "r_b", "bot_user", "Bot", 1, 100, 5, "2024-01-01", "", True)
        human = PlatformSampleAccount("reddit", "r_h", "human_user", "Human", 100, 100, 50, "2024-01-01", "", False)
        result = E2EPipelineVerifier.run_pipeline([bot, human])
        self.assertEqual(result.cytoscape_report.risk_distribution["bot"], 1)
        self.assertEqual(result.cytoscape_report.risk_distribution["human"], 1)


if __name__ == "__main__":
    unittest.main()
