import sqlite3
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from sbh.contracts.capabilities import default_registry
from sbh.shared.errors import ConfigError, InvalidTransitionError, SbhError
from sbh.storage.analysis import AnalysisRepository
from sbh.storage.capabilities import sync_registry
from sbh.storage.database import SQLiteDatabase, to_pyformat
from sbh.storage.migrate import apply_migrations, default_migrations_dir
from sbh.storage.scans import ALLOWED, ScanRepository
from tests.support import DbTestCase

NOW = "2026-09-30T12:00:00.000000Z"
T = datetime(2026, 9, 30, 12, tzinfo=UTC)


class Migrations(unittest.TestCase):
    def test_apply_is_idempotent_and_recorded(self):
        db = SQLiteDatabase()
        self.assertEqual(apply_migrations(db), ["0001_init"])
        self.assertEqual(apply_migrations(db), [])
        row = db.query_one("SELECT COUNT(*) AS n FROM schema_migrations")
        self.assertEqual(row["n"], 1)

    def test_editing_an_applied_migration_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            src = (default_migrations_dir() / "0001_init.sql").read_text()
            (Path(d) / "0001_init.sql").write_text(src)
            db = SQLiteDatabase()
            apply_migrations(db, Path(d))
            (Path(d) / "0001_init.sql").write_text(src + "\n-- tampered\n")
            with self.assertRaisesRegex(SbhError, "modified after being applied"):
                apply_migrations(db, Path(d))

    def test_failed_migration_rolls_back_completely(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "0001_bad.sql").write_text("CREATE TABLE ok_table (id TEXT);\nCREATE TABLE ok_table (id TEXT);")
            db = SQLiteDatabase()
            with self.assertRaises(sqlite3.OperationalError):
                apply_migrations(db, Path(d))
            tables = {r["name"] for r in db.query_all("SELECT name FROM sqlite_master WHERE type='table'")}
            self.assertNotIn("ok_table", tables)
            self.assertEqual(db.query_one("SELECT COUNT(*) AS n FROM schema_migrations")["n"], 0)

    def test_placeholder_rewrite_for_postgres(self):
        self.assertEqual(to_pyformat("SELECT :a, :b_2 WHERE x = 5 % 2"), "SELECT %(a)s, %(b_2)s WHERE x = 5 %% 2")
        # casts and time-of-day text are not parameters
        self.assertEqual(to_pyformat("SELECT x::text, '12:30'"), "SELECT x::text, '12:30'")


class Constraints(DbTestCase):
    """The database itself must reject states the application should never produce."""

    def setUp(self):
        super().setUp()
        self.scans = ScanRepository(self.db, lambda: T)
        self.scan = self.scans.create_scan(scan_type="dataset_import", collection_mode="dataset_import",
                                           platform="x", data_origin="synthetic", requested_by="t",
                                           reference_time=T, config_version="v", config_sha256="h")
        for pid in ("a", "b"):
            self.db.execute("INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, "
                            "last_observed_at, first_seen_scan_id, metadata, provenance) VALUES "
                            "(:id, 'x', :id, :t, :t, :s, '{}', 'test')", {"id": pid, "t": NOW, "s": self.scan})

    def insert_edge(self, i, src="a", dst="b", **over):
        p = {"id": i, "s": self.scan, "src": src, "dst": dst, "t": NOW, "type": "follows", "vs": "unverified"}
        p.update(over)
        self.db.execute("INSERT INTO relationship_edges (id, scan_id, platform, source_account_id, target_account_id, "
                        "relationship_type, observed_at, collected_at, verification_status, provenance) VALUES "
                        "(:id, :s, 'x', :src, :dst, :type, :t, :t, :vs, 'test')", p)

    def test_edge_uniqueness_self_loop_and_foreign_keys(self):
        self.insert_edge("e1")
        with self.assertRaises(sqlite3.IntegrityError):
            self.insert_edge("e2")                                   # same grain twice
        self.insert_edge("e3", src="b", dst="a")                      # the reverse is a different edge
        with self.assertRaises(sqlite3.IntegrityError):
            self.insert_edge("e4", src="a", dst="a")                  # self follow
        with self.assertRaises(sqlite3.IntegrityError):
            self.insert_edge("e5", dst="nobody")                      # FK
        with self.assertRaises(sqlite3.IntegrityError):
            self.insert_edge("e6", type="blocks")                     # enum

    def test_account_identity_is_unique_per_platform_account(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, "
                            "last_observed_at, first_seen_scan_id, metadata, provenance) VALUES "
                            "('dup', 'x', 'a', :t, :t, :s, '{}', 'x')", {"t": NOW, "s": self.scan})
        # the same id on another platform is a different account
        self.db.execute("INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, "
                        "last_observed_at, first_seen_scan_id, metadata, provenance) VALUES "
                        "('other', 'tiktok', 'a', :t, :t, :s, '{}', 'x')", {"t": NOW, "s": self.scan})

    def test_negative_counts_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO account_observations (id, platform_account_id, scan_id, observed_at, "
                            "collected_at, follower_count, source_payload_sha256, provenance) VALUES "
                            "('o', 'a', :s, :t, :t, -1, 'h', 'p')", {"s": self.scan, "t": NOW})

    def test_feature_is_either_available_with_value_or_unavailable_without(self):
        def feat(i, value, avail):
            self.db.execute("INSERT INTO account_features (id, scan_id, platform_account_id, feature_name, "
                            "feature_version, category, value, is_available, details, computed_at) VALUES "
                            "(:i, :s, 'a', :n, 'v1', 'profile', :v, :a, '{}', :t)",
                            {"i": i, "s": self.scan, "n": i, "v": value, "a": avail, "t": NOW})
        feat("ok1", 1.0, True)
        feat("ok2", None, False)
        with self.assertRaises(sqlite3.IntegrityError):
            feat("bad1", None, True)       # available but no value
        with self.assertRaises(sqlite3.IntegrityError):
            feat("bad2", 0.0, False)       # unavailable must not carry a (zero) value

    def test_assessment_state_constraints(self):
        mv = AnalysisRepository(self.db).register_model_version(kind="rules", name="n", version="v", config={}, config_sha256="h")

        def assess(i, status, score, band):
            self.db.execute("INSERT INTO risk_assessments (id, scan_id, platform_account_id, feature_version, "
                            "model_version_id, status, score, band, evidence_coverage, features_available, "
                            "features_total, contributions, limitations, assessed_at) VALUES "
                            "(:i, :s, :a, 'f', :m, :st, :sc, :b, 0.5, 1, 2, '[]', '[]', :t)",
                            {"i": i, "s": self.scan, "a": i[0], "m": mv, "st": status, "sc": score, "b": band, "t": NOW})
        assess("a1", "scored", 50.0, "elevated")
        with self.assertRaises(sqlite3.IntegrityError):
            assess("b1", "scored", None, None)                     # a scored assessment needs a score
        with self.assertRaises(sqlite3.IntegrityError):
            assess("a2", "insufficient_evidence", 10.0, None)      # no score allowed without evidence
        with self.assertRaises(sqlite3.IntegrityError):
            assess("b2", "scored", 150.0, "x")                     # out of range

    def test_database_refuses_verified_capability_without_evidence(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO platform_capabilities (platform, operation, collection_mode, status, "
                            "required_scopes, credentials_required, limitations, updated_at) VALUES "
                            "('x', 'list_followers', 'official_api', 'verified', '[]', '[]', '[]', :t)", {"t": NOW})

    def test_registry_sync_is_idempotent(self):
        n = sync_registry(self.db, default_registry())
        sync_registry(self.db, default_registry())
        self.assertEqual(self.count("platform_capabilities"), n)

    def test_model_version_reuse_with_changed_config_is_refused(self):
        repo = AnalysisRepository(self.db)
        a = repo.register_model_version(kind="rules", name="n", version="v1", config={"w": 1}, config_sha256="aaa")
        self.assertEqual(a, repo.register_model_version(kind="rules", name="n", version="v1", config={"w": 1}, config_sha256="aaa"))
        with self.assertRaises(ConfigError):
            repo.register_model_version(kind="rules", name="n", version="v1", config={"w": 2}, config_sha256="bbb")


class ScanStateMachine(DbTestCase):
    def setUp(self):
        super().setUp()
        self.repo = ScanRepository(self.db, lambda: T)
        self.sid = self.repo.create_scan(scan_type="dataset_import", collection_mode="dataset_import", platform="x",
                                         data_origin="imported", requested_by="t", reference_time=T,
                                         config_version="v", config_sha256="h")

    def status(self):
        return self.repo.get_scan(self.sid)["status"]

    def test_happy_path_sets_timestamps(self):
        self.repo.transition(self.sid, "running", ["pending"])
        s = self.repo.get_scan(self.sid)
        self.assertIsNotNone(s["started_at"])
        self.assertIsNone(s["finished_at"])
        self.repo.transition(self.sid, "complete", ["running"], completeness="complete")
        s = self.repo.get_scan(self.sid)
        self.assertEqual((s["status"], s["collection_completeness"]), ("complete", "complete"))
        self.assertIsNotNone(s["finished_at"])

    def test_wrong_source_state_is_rejected_and_changes_nothing(self):
        with self.assertRaises(InvalidTransitionError):
            self.repo.transition(self.sid, "complete", ["running"])   # still pending
        self.assertEqual(self.status(), "pending")

    def test_second_worker_cannot_win_the_same_transition(self):
        self.repo.transition(self.sid, "running", ["pending"])
        with self.assertRaises(InvalidTransitionError):
            self.repo.transition(self.sid, "running", ["pending"])

    def test_terminal_states_are_final_except_failed_which_can_resume(self):
        for terminal in ("complete", "partial", "cancelled"):
            self.assertEqual(ALLOWED[terminal], frozenset())
        self.repo.transition(self.sid, "running", ["pending"])
        self.repo.transition(self.sid, "failed", ["running"], failure_reason="boom")
        self.assertEqual(self.repo.get_scan(self.sid)["failure_reason"], "boom")
        self.repo.transition(self.sid, "running", ["failed"])
        s = self.repo.get_scan(self.sid)
        self.assertEqual((s["status"], s["failure_reason"], s["finished_at"]), ("running", None, None))

    def test_programmer_errors_are_caught(self):
        with self.assertRaises(ValueError):
            self.repo.transition(self.sid, "complete", ["pending"])   # pending can never go straight to complete

    def test_awaiting_access_approval_is_a_real_state(self):
        self.repo.transition(self.sid, "awaiting_access_approval", ["pending"])
        self.repo.transition(self.sid, "running", ["awaiting_access_approval"])

    def test_checkpoints_upsert(self):
        self.repo.set_checkpoint(self.sid, "persist", 500, False)
        self.repo.set_checkpoint(self.sid, "persist", 900, True)
        self.assertEqual(self.repo.get_checkpoint(self.sid, "persist"), (900, True))
        self.assertIsNone(self.repo.get_checkpoint(self.sid, "other"))


if __name__ == "__main__":
    unittest.main()
