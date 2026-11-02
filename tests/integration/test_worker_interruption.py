"""Simulated worker process interruption and multi-stage checkpoint recovery tests."""

import unittest
from unittest import mock

from sbh.config import load_config
from sbh.pipeline.run import import_dataset
from sbh.shared.errors import ScanFailedError
from sbh.storage.accounts import AccountRepository
from sbh.storage.edges import EdgeRepository
from sbh.storage.scans import ScanRepository
from tests.integration.test_pipeline_reliability import signature, small_cfg
from tests.support import DbTestCase, make_db, synthetic_dir

CFG = load_config()


class WorkerInterruptionAndRecoveryTests(DbTestCase):
    def test_interruption_at_accounts_stage_resumes_cleanly(self):
        cfg = small_cfg(20)
        original_insert = AccountRepository.insert_observations
        call_count = 0

        def crash_on_second_account_batch(self_, *a, **k):
            nonlocal call_count
            original_insert(self_, *a, **k)
            call_count += 1
            if call_count == 2:
                raise RuntimeError("simulated SIGKILL / worker crash during accounts stage")

        with (
            mock.patch.object(AccountRepository, "insert_observations", crash_on_second_account_batch),
            self.assertRaises(ScanFailedError) as ctx,
        ):
            import_dataset(self.db, synthetic_dir(), cfg)

        sid = ctx.exception.scan_id
        scans = ScanRepository(self.db)
        scan = scans.get_scan(sid)
        self.assertEqual(scan["status"], "failed")

        # Observations checkpoint should reflect exactly 1 batch committed
        chk = scans.get_checkpoint(sid, "persist_observations")
        self.assertIsNotNone(chk)
        self.assertEqual(chk[0], 20)
        self.assertFalse(chk[1])

        # Resume the interrupted scan
        resumed = import_dataset(self.db, synthetic_dir(), cfg)
        self.assertEqual(resumed.scan_id, sid)
        self.assertEqual(resumed.status, "partial")

        # Compare with clean baseline run on fresh DB
        clean_db, cleanup = make_db()
        self.addCleanup(clean_db.close)
        clean_res = import_dataset(clean_db, synthetic_dir(), cfg)

        # Assert zero data loss, zero duplicated rows, identical signature
        self.assertEqual(
            self.count("account_observations", "scan_id = :s", s=sid),
            clean_db.query_one("SELECT COUNT(*) AS c FROM account_observations WHERE scan_id = :s", {"s": clean_res.scan_id})["c"],
        )
        self.assertEqual(
            self.count("relationship_edges", "scan_id = :s", s=sid),
            clean_db.query_one("SELECT COUNT(*) AS c FROM relationship_edges WHERE scan_id = :s", {"s": clean_res.scan_id})["c"],
        )
        self.assertEqual(signature(self.db, sid), signature(clean_db, clean_res.scan_id))

    def test_interruption_at_edges_stage_resumes_without_duplicate_edges(self):
        cfg = small_cfg(50)
        original_insert_edges = EdgeRepository.insert_edges
        edge_calls = 0

        def crash_on_third_edge_batch(self_, *a, **k):
            nonlocal edge_calls
            original_insert_edges(self_, *a, **k)
            edge_calls += 1
            if edge_calls == 3:
                raise RuntimeError("simulated worker crash during edges stage")

        with (
            mock.patch.object(EdgeRepository, "insert_edges", crash_on_third_edge_batch),
            self.assertRaises(ScanFailedError) as ctx,
        ):
            import_dataset(self.db, synthetic_dir(), cfg)

        sid = ctx.exception.scan_id
        scans = ScanRepository(self.db)
        self.assertEqual(scans.get_scan(sid)["status"], "failed")
        self.assertEqual(scans.get_checkpoint(sid, "persist_relationships"), (100, False))

        # Resume
        resumed = import_dataset(self.db, synthetic_dir(), cfg)
        self.assertEqual(resumed.scan_id, sid)
        self.assertTrue(scans.get_checkpoint(sid, "persist_relationships")[1])

        # Check total edges match baseline
        clean_db, cleanup = make_db()
        self.addCleanup(clean_db.close)
        clean_res = import_dataset(clean_db, synthetic_dir(), cfg)

        self.assertEqual(
            self.count("relationship_edges", "scan_id = :s", s=sid),
            clean_db.query_one("SELECT COUNT(*) AS c FROM relationship_edges WHERE scan_id = :s", {"s": clean_res.scan_id})["c"],
        )
        self.assertEqual(signature(self.db, sid), signature(clean_db, clean_res.scan_id))


if __name__ == "__main__":
    unittest.main()
