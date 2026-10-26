"""Dataset -> validation -> persistence -> features -> scores -> clusters -> evidence, on the
synthetic demo data. These are regression checks that the pipeline finds what was planted;
they are NOT a measurement of accuracy on real accounts (see docs/model-card.md)."""

import csv
import unittest

from sbh.config import load_config
from sbh.fixtures import synthetic
from sbh.graph.compare import diff_edge_sets
from sbh.pipeline.run import import_dataset
from sbh.storage.analysis import AnalysisRepository
from sbh.storage.edges import EdgeRepository
from sbh.storage.scans import ScanRepository
from tests.support import make_db, synthetic_dir


class EndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = load_config()
        cls.db, cls._cleanup = make_db()
        cls.res = import_dataset(cls.db, synthetic_dir(), cls.cfg, requested_by="test")
        cls.repo = AnalysisRepository(cls.db)
        cls.truth = synthetic.generate(42).truth
        cls.assess = {a["pid"]: a for a in cls.repo.list_assessments(cls.res.scan_id)}
        cls.clusters = cls.repo.list_clusters(cls.res.scan_id)

    @classmethod
    def tearDownClass(cls):
        cls._cleanup()

    def n(self, table, where="1=1", **p):
        return self.db.query_one(f"SELECT COUNT(*) AS n FROM {table} WHERE {where}", p)["n"]

    # ------------------------------------------------------------------ scan outcome
    def test_scan_is_partial_because_followers_lists_are_declared_partial(self):
        scan = ScanRepository(self.db).get_scan(self.res.scan_id)
        self.assertEqual(scan["status"], "partial")
        self.assertEqual(scan["collection_completeness"], "partial")
        self.assertEqual(scan["data_origin"], "synthetic")
        self.assertTrue(any("completeness is 'partial'" in r for r in scan["status_detail"]["partial_reasons"]))
        self.assertEqual(self.n("quarantined_records"), 0)

    def test_persisted_rows_match_the_input_files(self):
        def rows(name):
            with (synthetic_dir() / name).open(newline="", encoding="utf-8") as fh:
                return list(csv.DictReader(fh))
        self.assertEqual(self.n("relationship_edges"), len(rows("relationships.csv")))
        self.assertEqual(self.n("content_observations"), len(rows("content.csv")))
        self.assertEqual(self.n("account_observations"), len(rows("accounts.csv")))

    def test_edges_are_directed_exactly_as_supplied(self):
        with (synthetic_dir() / "relationships.csv").open(newline="", encoding="utf-8") as fh:
            supplied = {(r["source_account_id"], r["target_account_id"]) for r in csv.DictReader(fh)}
        stored = set(EdgeRepository(self.db).load_edges(self.res.scan_id))
        self.assertEqual(stored, supplied)
        one_way = next(e for e in sorted(supplied) if (e[1], e[0]) not in supplied)
        self.assertNotIn((one_way[1], one_way[0]), stored)  # reverse never inferred

    def test_stub_accounts_have_no_invented_profile_data(self):
        self.assertEqual(self.n("account_observations o JOIN platform_accounts a ON a.id = o.platform_account_id",
                                "a.platform_account_id LIKE 'b0%'"), 0)
        self.assertEqual(self.n("platform_accounts"), self.res.summary["accounts_in_scan"])

    def test_missing_values_stay_null_never_zero(self):
        rows = self.db.query_all(
            "SELECT a.platform_account_id AS pid, o.follower_count FROM account_observations o "
            "JOIN platform_accounts a ON a.id = o.platform_account_id WHERE a.platform_account_id IN ('s001', 's002')")
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(r["follower_count"] is None for r in rows))

    # ------------------------------------------------------------------ account assessments
    def test_planted_bots_score_high_organic_accounts_low(self):
        for pid in self.truth["ring_obvious"]:
            self.assertGreaterEqual(self.assess[pid]["score"], 75, pid)
            self.assertEqual(self.assess[pid]["band"], "strong_combination_of_indicators")
        for pid in self.truth["ring_stealth"]:
            self.assertGreaterEqual(self.assess[pid]["score"], 50, pid)
        for pid in self.truth["organic"]:
            self.assertLess(self.assess[pid]["score"], 25, pid)
        for pid in self.truth["friends"]:
            self.assertLess(self.assess[pid]["score"], 50, pid)

    def test_accounts_without_enough_evidence_get_no_score(self):
        for group in ("hubs", "sparse", "promoted"):
            for pid in self.truth[group]:
                a = self.assess[pid]
                self.assertEqual(a["status"], "insufficient_evidence", pid)
                self.assertIsNone(a["score"])
                self.assertTrue(any("Insufficient evidence" in x for x in a["limitations"]))
        self.assertEqual(self.res.summary["assessments_scored"] + self.res.summary["assessments_insufficient_evidence"],
                         self.res.summary["accounts_in_scan"])

    def test_every_assessment_is_traceable_and_explainable(self):
        mv_ids = {r["id"] for r in self.db.query_all("SELECT id FROM model_versions")}
        for a in self.assess.values():
            self.assertIn(a["model_version_id"], mv_ids)
            self.assertEqual(a["feature_version"], "features-v1")
            self.assertTrue(0.0 <= a["evidence_coverage"] <= 1.0)
            self.assertTrue(a["limitations"])
            if a["status"] == "scored":
                pts = sum(c["points"] for c in a["contributions"] if c["available"])
                self.assertAlmostEqual(pts, a["score"], delta=0.05, msg=a["pid"])

    def test_score_is_backed_by_evidence_records_with_source_references(self):
        scored = [a for a in self.assess.values() if a["status"] == "scored" and a["score"] > 0]
        self.assertTrue(scored)
        for a in scored:
            ev = self.repo.list_evidence(self.res.scan_id, "account", a["platform_account_id"])
            self.assertTrue(ev, a["pid"])
            for e in ev:
                self.assertTrue(e["source_refs"])
                self.assertEqual(e["model_version_id"], a["model_version_id"])
            self.assertAlmostEqual(sum(e["details"]["points"] for e in ev), a["score"], delta=0.05)

    def test_features_table_distinguishes_unavailable_from_zero(self):
        rows = self.db.query_all(
            "SELECT f.is_available, f.value, f.unavailable_reason FROM account_features f "
            "JOIN platform_accounts a ON a.id = f.platform_account_id WHERE a.platform_account_id = 'h001'")
        self.assertTrue(rows)
        for r in rows:
            if not r["is_available"]:
                self.assertIsNone(r["value"])
                self.assertTrue(r["unavailable_reason"])

    # ------------------------------------------------------------------ clusters
    def test_bot_ring_found_as_a_high_strength_cluster(self):
        ring = set(self.truth["ring_obvious"]) | set(self.truth["ring_stealth"])
        (c,) = [c for c in self.clusters if set(c["members"]) == ring]
        self.assertEqual(c["signal_strength"], "high")
        for signal in ("content_duplication", "temporal_synchrony", "member_risk"):
            self.assertTrue(c["signals"][signal]["signal_present"], signal)
        self.assertGreater(c["signals"]["temporal_synchrony"]["lift"], 50)
        self.assertEqual(c["signals"]["content_duplication"]["cross_member_duplicate_ratio"], 1.0)

    def test_friend_group_is_surfaced_but_only_as_low_strength_with_alternatives(self):
        (c,) = [c for c in self.clusters if set(c["members"]) == set(self.truth["friends"])]
        self.assertEqual(c["signal_strength"], "low")
        self.assertFalse(any(c["signals"][s]["signal_present"]
                             for s in ("content_duplication", "temporal_synchrony", "member_risk")))
        text = " ".join(c["alternative_explanations"])
        self.assertIn("follow each other mutually", text)
        self.assertIn("popular accounts", text)

    def test_every_cluster_records_method_coverage_uncertainty_and_review_status(self):
        self.assertEqual(len(self.clusters), 2)
        for c in self.clusters:
            self.assertEqual((c["method"], c["review_status"]), ("similarity-louvain", "unreviewed"))
            self.assertIn(c["confidence"], ("low", "moderate"))   # never "high" from automation alone
            self.assertTrue(c["uncertainty_notes"] and c["alternative_explanations"] and c["coverage"])
            self.assertEqual(c["member_count"], len(c["members"]))
            ev = self.repo.list_evidence(self.res.scan_id, "cluster", c["id"])
            self.assertIn("structural_similarity", {e["evidence_type"] for e in ev})
            self.assertIn("coverage", {e["evidence_type"] for e in ev})

    def test_cluster_members_reference_real_accounts(self):
        self.assertEqual(self.n("cluster_memberships m LEFT JOIN platform_accounts a ON a.id = m.platform_account_id",
                                "a.id IS NULL"), 0)

    # ------------------------------------------------------------------ audit, idempotency, history
    def test_audit_trail_records_scan_lifecycle(self):
        actions = {r["action"] for r in self.db.query_all("SELECT action FROM audit_events")}
        self.assertTrue({"scan_created", "scan_finished"} <= actions)

    def test_importing_the_same_input_again_changes_nothing(self):
        before = {t: self.n(t) for t in ("scan_jobs", "relationship_edges", "account_observations",
                                         "content_observations", "risk_assessments", "platform_accounts")}
        again = import_dataset(self.db, synthetic_dir(), self.cfg, requested_by="test")
        after = {t: self.n(t) for t in before}
        self.assertTrue(again.already_imported)
        self.assertEqual(again.scan_id, self.res.scan_id)
        self.assertEqual(before, after)


class JsonBundleEquivalence(unittest.TestCase):
    def test_json_bundle_gives_identical_results_and_scan_history_shows_no_change(self):
        import tempfile
        from pathlib import Path
        db, cleanup = make_db()
        self.addCleanup(cleanup)
        cfg = load_config()
        r1 = import_dataset(db, synthetic_dir(), cfg)
        with tempfile.TemporaryDirectory() as d:
            bundle = synthetic.write_json_bundle(synthetic.generate(42), Path(d) / "bundle.json")
            r2 = import_dataset(db, bundle, cfg)
        self.assertNotEqual(r1.scan_id, r2.scan_id)           # different bytes, so a new scan
        repo = AnalysisRepository(db)
        s1 = {a["pid"]: (a["status"], a["score"]) for a in repo.list_assessments(r1.scan_id)}
        s2 = {a["pid"]: (a["status"], a["score"]) for a in repo.list_assessments(r2.scan_id)}
        self.assertEqual(s1, s2)
        self.assertEqual(r1.summary["candidate_clusters"], r2.summary["candidate_clusters"])
        # one persisted identity per platform account, however many scans saw it
        self.assertEqual(db.query_one("SELECT COUNT(*) AS n FROM platform_accounts")["n"], r1.summary["accounts_in_scan"])
        er = EdgeRepository(db)
        diff = diff_edge_sets(set(er.load_edges(r1.scan_id)), set(er.load_edges(r2.scan_id)),
                              {k: v.completeness for k, v in er.load_coverage(r1.scan_id).items()},
                              {k: v.completeness for k, v in er.load_coverage(r2.scan_id).items()})
        self.assertEqual({k: v for k, v in diff.summary().items() if k != "unchanged"},
                         {"confirmed_added": 0, "newly_observed": 0, "confirmed_removed": 0, "not_reobserved": 0})


if __name__ == "__main__":
    unittest.main()
