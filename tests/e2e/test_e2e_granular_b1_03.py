"""Granular test 3 for unicode and emoji character safety."""

from __future__ import annotations

import unittest
from sbh.e2e.pipeline import E2EPipelineVerifier
from sbh.e2e.platforms import PlatformSampleAccount


class TestE2EGranularB103(unittest.TestCase):
    def test_unicode_and_emojis_in_labels(self):
        acc = PlatformSampleAccount("mastodon", "m_jp", "ユーザー_🤖", "山田太郎", 50, 50, 10, "2024-01-01", "東京 🗼", False)
        result = E2EPipelineVerifier.run_pipeline([acc])
        self.assertTrue(result.success)
        node_label = result.cytoscape_elements["nodes"][0]["data"]["label"]
        self.assertEqual(node_label, "ユーザー_🤖")


if __name__ == "__main__":
    unittest.main()
