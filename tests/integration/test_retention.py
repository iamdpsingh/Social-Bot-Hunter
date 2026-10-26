import unittest
from datetime import UTC, datetime

from sbh.pipeline.run import import_dataset
from sbh.shared.errors import SbhError
from sbh.storage.retention import delete_scan, delete_scans_older_than
from tests.support import DbTestCase, acct, edge, manifest, post, synthetic_dir, write_dir
from sbh.config import load_config

CFG = load_config()
TABLES = ("relationship_edges", "account_observations", "content_observations", "account_features",
          "risk_assessments", "network_clusters", "cluster_memberships", "evidence_records",
          "relationship_list_coverage", "quarantined_records", "scan_checkpoints", "dataset_imports",
          "platform_accounts", "scan_jobs")


class Deletion(DbTestCase):
    def counts(self):
        return {t: self.count(t) for t in TABLES}

    def test_deleting_the_only_scan_removes_all_derived_and_personal_data(self):
        res = import_dataset(self.db, synthetic_dir(), CFG)
        deleted = delete_scan(self.db, res.scan_id, actor="privacy-officer")
        self.assertEqual(self.counts(), {t: 0 for t in TABLES})
        self.assertGreater(deleted["relationship_edges"], 0)
        audit = self.db.query_one("SELECT * FROM audit_events WHERE action = 'scan_deleted'")
        self.assertEqual(audit["actor"], "privacy-officer")      # the audit trail survives deletion
        self.assertEqual(self.count("model_versions") > 0, True)  # configuration is not personal data

    def test_deletion_frees_the_input_so_it_can_be_imported_again(self):
        res = import_dataset(self.db, synthetic_dir(), CFG)
        delete_scan(self.db, res.scan_id, "t")
        again = import_dataset(self.db, synthetic_dir(), CFG)
        self.assertFalse(again.already_imported)
        self.assertNotEqual(again.scan_id, res.scan_id)

    def test_accounts_still_used_by_another_scan_are_kept(self):
        a = write_dir(self.tmp / "a", man=manifest(dataset_name="a"), accounts=[acct("shared"), acct("only_a")],
                      relationships=[edge("shared", "only_a")])
        b = write_dir(self.tmp / "b", man=manifest(dataset_name="b"), accounts=[acct("shared", follower_count=5)],
                      relationships=[], content=[post("c1", "shared", "2026-09-29T00:00:00Z", "some words to fingerprint here")])
        ra, rb = import_dataset(self.db, a, CFG), import_dataset(self.db, b, CFG)
        delete_scan(self.db, ra.scan_id, "t")
        names = {r["platform_account_id"] for r in self.db.query_all("SELECT platform_account_id FROM platform_accounts")}
        self.assertEqual(names, {"shared"})                       # only_a was orphaned and removed
        self.assertEqual(self.count("account_observations", "scan_id = :s", s=rb.scan_id), 1)
        self.assertEqual(self.count("scan_jobs"), 1)
        self.assertIsNone(self.db.query_one("SELECT first_seen_scan_id AS f FROM platform_accounts")["f"])

    def test_running_scans_are_not_deleted_and_unknown_scans_error(self):
        res = import_dataset(self.db, synthetic_dir(), CFG)
        self.db.execute("UPDATE scan_jobs SET status = 'running' WHERE id = :s", {"s": res.scan_id})
        with self.assertRaisesRegex(SbhError, "is running"):
            delete_scan(self.db, res.scan_id, "t")
        with self.assertRaisesRegex(SbhError, "no such scan"):
            delete_scan(self.db, "nope", "t")

    def test_a_failing_deletion_leaves_everything_in_place(self):
        res = import_dataset(self.db, synthetic_dir(), CFG)
        before = self.counts()
        from unittest import mock
        from sbh.storage.scans import ScanRepository
        with mock.patch.object(ScanRepository, "audit", side_effect=RuntimeError("audit store down")):
            with self.assertRaises(RuntimeError):
                delete_scan(self.db, res.scan_id, "t")
        self.assertEqual(self.counts(), before)                   # all-or-nothing

    def test_retention_sweep_deletes_only_old_finished_scans(self):
        long_ago = lambda: datetime(2026, 4, 1, tzinfo=UTC)       # noqa: E731
        recent = lambda: datetime(2026, 9, 30, 13, tzinfo=UTC)    # noqa: E731
        sweep_time = lambda: datetime(2026, 10, 1, tzinfo=UTC)    # noqa: E731
        old = import_dataset(self.db, write_dir(self.tmp / "o", man=manifest(dataset_name="o", collected_at="2026-03-30T00:00:00Z"),
                                                accounts=[acct("old", observed_at="2026-03-29T00:00:00Z")]), CFG, clock=long_ago)
        new = import_dataset(self.db, write_dir(self.tmp / "n", man=manifest(dataset_name="n"), accounts=[acct("new")]),
                             CFG, clock=recent)
        deleted = delete_scans_older_than(self.db, 90, "retention-job", clock=sweep_time)
        self.assertEqual(deleted, [old.scan_id])
        self.assertEqual({r["id"] for r in self.db.query_all("SELECT id FROM scan_jobs")}, {new.scan_id})
        with self.assertRaises(ValueError):
            delete_scans_older_than(self.db, 0, "x")


if __name__ == "__main__":
    unittest.main()
