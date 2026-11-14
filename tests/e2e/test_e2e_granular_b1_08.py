"""Granular test 8 for node metadata fields."""

from __future__ import annotations

import unittest

from sbh.e2e.pipeline import E2EPipelineVerifier
from sbh.e2e.platforms import PlatformSampleAccount


class TestE2EGranularB108(unittest.TestCase):
    def test_node_metadata_fields(self):
        acc = PlatformSampleAccount("mastodon", "m1", "mast_user", "Mast", 250, 180, 50, "2024-01-01", "Bio", False)
        result = E2EPipelineVerifier.run_pipeline([acc])
        node_data = result.cytoscape_elements["nodes"][0]["data"]
        self.assertEqual(node_data["platform"], "mastodon")
        self.assertEqual(node_data["followers_count"], 250)
        self.assertEqual(node_data["following_count"], 180)


if __name__ == "__main__":
    unittest.main()
