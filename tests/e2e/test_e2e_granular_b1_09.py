"""Granular test 9 for unassigned cluster fallback."""

from __future__ import annotations

import unittest

from sbh.e2e.pipeline import E2EPipelineVerifier
from sbh.e2e.platforms import PlatformSampleAccount


class TestE2EGranularB109(unittest.TestCase):
    def test_unassigned_cluster_id(self):
        acc = PlatformSampleAccount("bluesky", "bsky_solo", "solo_user", "Solo", 100, 100, 10, "2024-01-01", "", False)
        result = E2EPipelineVerifier.run_pipeline([acc])
        node_data = result.cytoscape_elements["nodes"][0]["data"]
        self.assertEqual(node_data["cluster_id"], "unassigned")


if __name__ == "__main__":
    unittest.main()
