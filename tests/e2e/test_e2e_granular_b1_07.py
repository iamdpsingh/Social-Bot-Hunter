"""Granular test 7 for follower ratio feature impact."""

from __future__ import annotations

import unittest

from sbh.e2e.pipeline import E2EPipelineVerifier
from sbh.e2e.platforms import PlatformSampleAccount


class TestE2EGranularB107(unittest.TestCase):
    def test_low_follower_ratio_elevates_risk(self):
        acc = PlatformSampleAccount("twitter", "low_ratio", "low_ratio_user", "User", 1, 1000, 10, "2024-01-01", "", True)
        result = E2EPipelineVerifier.run_pipeline([acc])
        self.assertGreaterEqual(result.risk_scores["low_ratio"], 0.85)


if __name__ == "__main__":
    unittest.main()
