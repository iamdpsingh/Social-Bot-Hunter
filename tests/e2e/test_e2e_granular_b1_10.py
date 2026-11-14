"""Granular test 10 for cluster serialization scaling."""

from __future__ import annotations

import time
import unittest

from sbh.e2e.pipeline import E2EPipelineVerifier
from sbh.e2e.platforms import MultiPlatformMockGenerator


class TestE2EGranularB110(unittest.TestCase):
    def test_serialization_speed_100_accounts(self):
        accounts = []
        for p in MultiPlatformMockGenerator.SUPPORTED_PLATFORMS:
            accounts.extend(MultiPlatformMockGenerator.generate_campaign_accounts(p, campaign_size=20))

        start = time.perf_counter()
        result = E2EPipelineVerifier.run_pipeline(accounts)
        elapsed = time.perf_counter() - start

        self.assertTrue(result.success)
        self.assertEqual(result.total_accounts, 100)
        self.assertLess(elapsed, 2.0, "100 accounts serialization should complete under 2s")


if __name__ == "__main__":
    unittest.main()
