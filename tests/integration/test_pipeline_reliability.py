import json
import unittest
from dataclasses import replace
from unittest import mock

from sbh.config import load_config
from sbh.fixtures import synthetic
from sbh.graph.compare import diff_edge_sets
from sbh.pipeline.run import import_dataset
from sbh.shared.errors import (
    InvalidTransitionError,
    ScanFailedError,
    ScanInProgressError,
    SchemaIncompatibleError,
)
from sbh.storage.analysis import AnalysisRepository
from sbh.storage.edges import EdgeRepository
from sbh.storage.scans import ScanRepository
from tests.support import DbTestCase, acct, edge, make_db, manifest, post, synthetic_dir, write_dir

CFG = load_config()


def small_cfg(batch=100):
    return replace(CFG, imports=replace(CFG.imports, batch_size=batch))


def signature(db, scan_id):
    repo = AnalysisRepository(db)
    return {
        "edges": EdgeRepository(db).load_edges(scan_id),
        "assessments": sorted((a["pid"], a["status"], a["score"]) for a in repo.list_assessments(scan_id)),
        "clusters": sorted(tuple(c["members"]) for c in repo.list_clusters(scan_id)),
    }


class InterruptedCollection(DbTestCase):
    def crash_on_third_edge_batch(self):
        original = EdgeRepository.insert_edges
        calls = []

        def flaky(self_, *a, **k):
            original(self_, *a, **k)            # the batch IS written...
            calls.append(1)
            if len(calls) == 3:
                raise RuntimeError("simulated worker crash after write")   # ...then the worker dies

        return mock.patch.object(EdgeRepository, "insert_edges", flaky)

    def test_failed_batch_rolls_back_and_resume_completes_identically_to_a_clean_run(self):
        cfg = small_cfg(100)
        with self.crash_on_third_edge_batch(), self.assertRaises(ScanFailedError) as ctx:
            import_dataset(self.db, synthetic_dir(), cfg)
        sid = ctx.exception.scan_id
        scans = ScanRepository(self.db)
        scan = scans.get_scan(sid)
        self.assertEqual(scan["status"], "failed")
        self.assertIn("RuntimeError", scan["failure_reason"])
        # two batches committed with their checkpoint; the crashed third batch left nothing behind
        self.assertEqual(scans.get_checkpoint(sid, "persist_relationships"), (200, False))
        self.assertEqual(self.count("relationship_edges", "scan_id = :s", s=sid), 200)
        self.assertEqual(self.count("risk_assessments"), 0)       # analysis never started on partial data

        resumed = import_dataset(self.db, synthetic_dir(), cfg)   # same input: resumes the failed scan
        self.assertEqual(resumed.scan_id, sid)
        self.assertEqual(resumed.status, "partial")
        self.assertFalse(resumed.already_imported)
        self.assertEqual(scans.get_checkpoint(sid, "persist_relationships")[1], True)
        self.assertEqual(self.count("scan_jobs"), 1)               # resumed, not duplicated
        detail = scans.get_scan(sid)["status_detail"]
        self.assertEqual(len(detail["failure_history"]), 1)
        actions = [r["action"] for r in self.db.query_all("SELECT action FROM audit_events")]
        self.assertIn("scan_resumed", actions)
        self.assertIn("scan_failed", actions)

        clean_db, cleanup = make_db()
        self.addCleanup(cleanup)
        clean = import_dataset(clean_db, synthetic_dir(), cfg)
        self.assertEqual(signature(self.db, sid), signature(clean_db, clean.scan_id))
        self.assertEqual(self.count("relationship_edges"), clean_db.query_one(
            "SELECT COUNT(*) AS n FROM relationship_edges")["n"])

    def test_scan_left_running_by_a_killed_worker_is_not_silently_taken_over(self):
        cfg = small_cfg(100)
        with self.crash_on_third_edge_batch(), self.assertRaises(ScanFailedError) as ctx:
            import_dataset(self.db, synthetic_dir(), cfg)
        sid = ctx.exception.scan_id
        self.db.execute("UPDATE scan_jobs SET status = 'running' WHERE id = :s", {"s": sid})  # as after kill -9
        with self.assertRaises(ScanInProgressError):
            import_dataset(self.db, synthetic_dir(), cfg)
        res = import_dataset(self.db, synthetic_dir(), cfg, allow_resume_running=True)
        self.assertEqual((res.scan_id, res.status), (sid, "partial"))

    def test_cancelled_scan_cannot_be_resumed(self):
        cfg = small_cfg(100)
        with self.crash_on_third_edge_batch(), self.assertRaises(ScanFailedError) as ctx:
            import_dataset(self.db, synthetic_dir(), cfg)
        self.db.execute("UPDATE scan_jobs SET status = 'cancelled' WHERE id = :s", {"s": ctx.exception.scan_id})
        with self.assertRaises(InvalidTransitionError):
            import_dataset(self.db, synthetic_dir(), cfg)

    def test_failure_is_recorded_on_the_scan_not_as_a_finding_about_accounts(self):
        with self.crash_on_third_edge_batch(), self.assertRaises(ScanFailedError):
            import_dataset(self.db, synthetic_dir(), small_cfg(100))
        self.assertEqual(self.count("risk_assessments") + self.count("network_clusters"), 0)


class InputProblems(DbTestCase):
    def test_unreadable_schema_creates_no_scan_but_is_audited(self):
        d = write_dir(self.tmp / "d", man=manifest(schema_version="9.0"), accounts=[acct("a")])
        with self.assertRaises(SchemaIncompatibleError):
            import_dataset(self.db, d, CFG, requested_by="tester")
        self.assertEqual(self.count("scan_jobs"), 0)
        row = self.db.query_one("SELECT * FROM audit_events WHERE action = 'import_rejected'")
        self.assertEqual(row["actor"], "tester")
        self.assertIn("schema_version", json.loads(row["details"])["reason"])

    def test_mostly_invalid_input_fails_the_scan_but_keeps_the_quarantine(self):
        rows = [acct(f"ok{i}") for i in range(3)] + [acct(f"bad{i}", follower_count=-1) for i in range(7)]
        d = write_dir(self.tmp / "d", man=manifest(), accounts=rows)
        with self.assertRaises(ScanFailedError) as ctx:
            import_dataset(self.db, d, CFG)
        self.assertIn("too_many_invalid_records", ctx.exception.reason)
        self.assertEqual(self.count("quarantined_records", "kind = 'invalid'"), 7)
        self.assertEqual(self.count("account_observations"), 0)        # nothing half-imported

    def test_dirty_data_is_quarantined_with_exact_counts_and_the_rest_is_kept(self):
        clean = synthetic.generate(42)
        dirty = synthetic.make_dirty(clean)
        from sbh.fixtures.synthetic import write_csv_dir
        res = import_dataset(self.db, write_csv_dir(dirty, self.tmp / "dirty"), CFG)
        self.assertEqual(res.status, "partial")
        scan = ScanRepository(self.db).get_scan(res.scan_id)
        self.assertTrue(any("9 record(s) rejected" in r for r in scan["status_detail"]["partial_reasons"]))
        q = {(r["entity"], r["kind"]): r["n"] for r in ScanRepository(self.db).quarantine_summary(res.scan_id)}
        self.assertEqual(q, {("account", "invalid"): 6, ("account", "duplicate"): 1,
                             ("relationship", "invalid"): 2, ("relationship", "duplicate"): 1,
                             ("content", "invalid"): 1})
        self.assertEqual(self.count("relationship_edges"), len(clean.relationships))   # all valid edges kept
        reasons = {r["reasons"] for r in self.db.query_all("SELECT reasons FROM quarantined_records")}
        flat = " ".join(reasons)
        for expected in ("negative_count:follower_count", "platform_mismatch", "future_timestamp:observed_at",
                         "self_relationship", "conflicting_duplicate", "duplicate_in_file", "missing_required"):
            self.assertIn(expected, flat)

    def test_unsupported_platform_in_manifest_is_rejected_before_any_scan(self):
        d = write_dir(self.tmp / "d", man=manifest(platform="myspace"), accounts=[acct("a")])
        with self.assertRaises(SchemaIncompatibleError):
            import_dataset(self.db, d, CFG)
        self.assertEqual(self.count("scan_jobs"), 0)


class OutcomeHonesty(DbTestCase):
    def tiny(self, name, coverage="complete", accounts=None, rels=None, content=None, **man):
        man.setdefault("relationship_coverage", {"default": coverage})
        return write_dir(self.tmp / name, man=manifest(**man),
                         accounts=accounts if accounts is not None else [acct("a"), acct("b")],
                         relationships=rels if rels is not None else [edge("a", "b")], content=content)

    def test_complete_requires_known_complete_coverage_and_no_rejections(self):
        res = import_dataset(self.db, self.tiny("ok"), CFG)
        self.assertEqual(res.status, "complete")
        scan = ScanRepository(self.db).get_scan(res.scan_id)
        self.assertEqual((scan["collection_completeness"], scan["status_detail"]["partial_reasons"]), ("complete", []))

    def test_unknown_coverage_is_never_reported_as_complete(self):
        res = import_dataset(self.db, self.tiny("unk", coverage="unknown"), CFG)
        self.assertEqual(res.status, "partial")
        self.assertEqual(ScanRepository(self.db).get_scan(res.scan_id)["collection_completeness"], "unknown")

    def test_dataset_without_any_relationships_has_unknown_completeness(self):
        res = import_dataset(self.db, self.tiny("norel", rels=[]), CFG)
        self.assertEqual(res.status, "partial")

    def test_a_rejected_record_makes_an_otherwise_complete_scan_partial(self):
        d = self.tiny("rej", accounts=[acct("a"), acct("b"), acct("c", follower_count=-1)] + [acct(f"x{i}") for i in range(20)])
        self.assertEqual(import_dataset(self.db, d, CFG).status, "partial")

    def test_expected_count_mismatch_downgrades_the_stored_coverage(self):
        ov = [{"platform_account_id": "a", "list_kind": "following", "completeness": "complete", "expected_count": 9}]
        d = self.tiny("pg", relationship_coverage={"default": "complete", "overrides": ov})
        res = import_dataset(self.db, d, CFG)
        row = self.db.query_one("SELECT completeness, observed_count, expected_count FROM relationship_list_coverage c "
                                "JOIN platform_accounts a ON a.id = c.platform_account_id "
                                "WHERE a.platform_account_id = 'a' AND c.list_kind = 'following'")
        self.assertEqual((row["completeness"], row["observed_count"], row["expected_count"]), ("partial", 1, 9))
        self.assertEqual(res.status, "partial")

    def test_zero_length_complete_list_is_recorded_as_a_real_zero(self):
        ov = [{"platform_account_id": "b", "list_kind": "following", "completeness": "complete", "expected_count": 0}]
        d = self.tiny("zero", relationship_coverage={"default": "partial", "overrides": ov})
        import_dataset(self.db, d, CFG)
        row = self.db.query_one("SELECT completeness, observed_count FROM relationship_list_coverage c "
                                "JOIN platform_accounts a ON a.id = c.platform_account_id "
                                "WHERE a.platform_account_id = 'b' AND c.list_kind = 'following'")
        self.assertEqual((row["completeness"], row["observed_count"]), ("complete", 0))

    def test_exceeding_graph_limits_degrades_to_partial_and_never_truncates_silently(self):
        tight = replace(CFG, graph=replace(CFG.graph, limits=replace(CFG.graph.limits, max_edges=100)))
        res = import_dataset(self.db, synthetic_dir(), tight)
        self.assertEqual(res.status, "partial")
        scan = ScanRepository(self.db).get_scan(res.scan_id)
        self.assertTrue(any("graph analysis skipped" in r for r in scan["status_detail"]["partial_reasons"]))
        self.assertIn("more than 100 edges", scan["status_detail"]["graph_error"])
        self.assertEqual(self.count("network_clusters"), 0)                        # no guessed clusters
        self.assertEqual(self.count("relationship_edges"), len(synthetic.generate(42).relationships))  # data still stored
        a = {x["pid"]: x for x in AnalysisRepository(self.db).list_assessments(res.scan_id)}
        # r001 still has profile/content evidence, so it is scored, but on reduced coverage and the
        # missing network evidence is disclosed rather than treated as zero
        self.assertEqual(a["r001"]["status"], "scored")
        self.assertAlmostEqual(a["r001"]["evidence_coverage"], 7.25 / 9.75, places=3)
        self.assertTrue(any("max_following_jaccard unavailable" in x for x in a["r001"]["limitations"]))
        jacc = self.db.query_one("SELECT is_available, unavailable_reason FROM account_features f "
                                 "JOIN platform_accounts p ON p.id = f.platform_account_id "
                                 "WHERE p.platform_account_id = 'r001' AND f.feature_name = 'max_following_jaccard'")
        self.assertFalse(jacc["is_available"])
        self.assertIn("no relationship data", jacc["unavailable_reason"])

    def test_row_count_change_between_imports_of_the_same_dataset_is_flagged(self):
        import_dataset(self.db, self.tiny("v1", accounts=[acct(f"a{i}") for i in range(10)], rels=[edge("a0", "a1")]), CFG)
        res = import_dataset(self.db, self.tiny("v2", accounts=[acct(f"a{i}") for i in range(30)], rels=[edge("a0", "a1")]), CFG)
        warnings = ScanRepository(self.db).get_scan(res.scan_id)["status_detail"]["data_quality_warnings"]
        self.assertTrue(any("accounts row count changed from 10 to 30" in w for w in warnings), warnings)


class HistoryAndRepeatedScans(DbTestCase):
    def v(self, name, accounts, rels, coverage="complete", overrides=None):
        cov = {"default": coverage, **({"overrides": overrides} if overrides else {})}
        return write_dir(self.tmp / name, man=manifest(relationship_coverage=cov), accounts=accounts, relationships=rels)

    def test_second_scan_adds_history_without_duplicating_identities(self):
        import_dataset(self.db, self.v("v1", [acct("a", username="old_name", observed_at="2026-09-01T00:00:00Z",
                                                 follower_count=10)], []), CFG)
        import_dataset(self.db, self.v("v2", [acct("a", username="new_name", observed_at="2026-09-20T00:00:00Z",
                                                 follower_count=90)], []), CFG)
        self.assertEqual(self.count("platform_accounts"), 1)
        self.assertEqual(self.count("account_observations"), 2)
        a = self.db.query_one("SELECT * FROM platform_accounts")
        self.assertEqual(a["username"], "new_name")            # mutable attribute follows the newest observation
        self.assertTrue(a["first_observed_at"] < a["last_observed_at"])
        names = [r["username"] for r in self.db.query_all("SELECT username FROM account_observations ORDER BY observed_at")]
        self.assertEqual(names, ["old_name", "new_name"])        # history preserved

    def test_older_observation_arriving_later_does_not_overwrite_the_current_username(self):
        import_dataset(self.db, self.v("new", [acct("a", username="new_name", observed_at="2026-09-20T00:00:00Z")], []), CFG)
        import_dataset(self.db, self.v("old", [acct("a", username="old_name", observed_at="2026-09-01T00:00:00Z")], []), CFG)
        self.assertEqual(self.db.query_one("SELECT username FROM platform_accounts")["username"], "new_name")

    def test_removal_is_confirmed_only_when_the_later_scan_has_a_complete_list(self):
        accts = [acct("a"), acct("b"), acct("c")]
        s1 = import_dataset(self.db, self.v("s1", accts, [edge("a", "b"), edge("a", "c")]), CFG)
        s2 = import_dataset(self.db, self.v("s2", accts, [edge("a", "b")], coverage="complete"), CFG)
        s3 = import_dataset(self.db, self.v("s3", accts, [edge("a", "b")], coverage="partial"), CFG)
        er = EdgeRepository(self.db)

        def diff(x, y):
            return diff_edge_sets(set(er.load_edges(x.scan_id)), set(er.load_edges(y.scan_id)),
                                  {k: v.completeness for k, v in er.load_coverage(x.scan_id).items()},
                                  {k: v.completeness for k, v in er.load_coverage(y.scan_id).items()})
        complete = diff(s1, s2)
        self.assertEqual(complete.confirmed_removed, {("a", "c")})
        partial = diff(s1, s3)
        self.assertEqual((partial.confirmed_removed, partial.not_reobserved), (set(), {("a", "c")}))

    def test_content_posted_in_two_scans_is_kept_per_scan(self):
        for name, extra in (("p1", "alpha"), ("p2", "beta")):
            d = write_dir(self.tmp / name, man=manifest(), accounts=[acct("a")], relationships=[],
                          content=[post("c1", "a", "2026-09-29T00:00:00Z", f"{extra} words here for testing fingerprints")])
            import_dataset(self.db, d, CFG)
        self.assertEqual(self.count("content_observations"), 2)


if __name__ == "__main__":
    unittest.main()
