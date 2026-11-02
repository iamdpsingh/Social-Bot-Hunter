"""Data quality tests for extreme counts, multi-language Unicode, boundary lengths, and null values."""

import unittest
from pathlib import Path

from sbh.config import load_config
from sbh.pipeline.run import import_dataset
from sbh.storage.accounts import AccountRepository
from sbh.storage.content import ContentRepository
from sbh.storage.scans import ScanRepository
from tests.support import DbTestCase

CFG = load_config()
EDGE_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "samples" / "edge_cases"


class EdgeCasesBenchmarkTests(DbTestCase):
    def test_import_edge_cases_benchmark_dataset(self):
        res = import_dataset(self.db, EDGE_DATA_DIR, CFG)
        self.assertEqual(res.status, "partial")
        self.assertTrue(res.summary["quarantined_records"] >= 3)

        acct_repo = AccountRepository(self.db)
        scan_repo = ScanRepository(self.db)
        cnt_repo = ContentRepository(self.db)

        # 1. 500M follower count (64-bit integer)
        id_map = acct_repo.scan_account_ids(res.scan_id)
        self.assertIn("edge_whale", id_map)
        obs_whale = self.db.query_one(
            "SELECT o.* FROM account_observations o JOIN platform_accounts a ON a.id = o.platform_account_id "
            "WHERE a.platform_account_id = 'edge_whale'"
        )
        self.assertIsNotNone(obs_whale)
        self.assertEqual(obs_whale["follower_count"], 500_000_000)
        self.assertEqual(obs_whale["following_count"], 100)

        # 2. Zero count is real zero, not None
        obs_zero = self.db.query_one(
            "SELECT o.* FROM account_observations o JOIN platform_accounts a ON a.id = o.platform_account_id "
            "WHERE a.platform_account_id = 'edge_zero'"
        )
        self.assertIsNotNone(obs_zero)
        self.assertEqual(obs_zero["follower_count"], 0)
        self.assertEqual(obs_zero["following_count"], 0)
        self.assertEqual(obs_zero["post_count"], 0)

        # 3. Unicode multi-lingual text preserved
        obs_unicode = self.db.query_one(
            "SELECT o.* FROM account_observations o JOIN platform_accounts a ON a.id = o.platform_account_id "
            "WHERE a.platform_account_id = 'edge_unicode'"
        )
        self.assertIsNotNone(obs_unicode)
        self.assertEqual(obs_unicode["display_name"], "日本語・العربية・हिन्दी")

        # 4. Handle leading @ stripped
        obs_at = self.db.query_one(
            "SELECT o.* FROM account_observations o JOIN platform_accounts a ON a.id = o.platform_account_id "
            "WHERE a.platform_account_id = 'edge_stripped'"
        )
        self.assertIsNotNone(obs_at)
        self.assertEqual(obs_at["username"], "at_handle")

        # 5. Invalid records quarantined with explicit reasons
        q_records = scan_repo.list_quarantined_records(res.scan_id)
        all_reasons = {reason for r in q_records for reason in r["reasons"]}
        self.assertIn("negative_count:follower_count", all_reasons)
        self.assertIn("future_timestamp:observed_at", all_reasons)
        self.assertIn("self_relationship", all_reasons)
        self.assertIn("future_timestamp:published_at", all_reasons)

        # 6. Content fingerprinting on multi-language content
        cnt_rows = [c for c in cnt_repo.load_content(res.scan_id) if c.author == "edge_unicode"]
        self.assertEqual(len(cnt_rows), 1)
        self.assertTrue(cnt_rows[0].content_hash)
        self.assertIsNotNone(cnt_rows[0].simhash)


if __name__ == "__main__":
    unittest.main()
