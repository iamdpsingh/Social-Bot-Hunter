"""Backend-agnostic pipeline run against a real PostgreSQL server.

SKIPPED unless SBH_TEST_POSTGRES_DSN is set (the build environment had no PostgreSQL, so this has
never been executed). Point it at a disposable database: it creates and drops a throw-away schema.
Until this passes, PostgreSQL support is unverified (see docs/status.md).
"""

import concurrent.futures
import unittest
import uuid

from sbh.config import load_config
from sbh.pipeline.run import import_dataset
from sbh.storage.database import PostgresPoolDatabase
from sbh.storage.migrate import apply_migrations
from tests.support import POSTGRES_DSN, make_db, synthetic_dir


@unittest.skipUnless(POSTGRES_DSN, "SBH_TEST_POSTGRES_DSN not set: PostgreSQL backend unverified")
class PostgresBackend(unittest.TestCase):
    def test_synthetic_pipeline_matches_expected_shape(self):
        db, cleanup = make_db()
        self.addCleanup(cleanup)
        res = import_dataset(db, synthetic_dir(), load_config())
        self.assertEqual(res.status, "partial")
        self.assertEqual(res.summary["candidate_clusters"], 2)
        again = import_dataset(db, synthetic_dir(), load_config())
        self.assertTrue(again.already_imported)

    def test_postgres_connection_pool_and_transactions(self):
        schema = f"sbh_pool_{uuid.uuid4().hex[:12]}"
        pool_db = PostgresPoolDatabase(POSTGRES_DSN, min_size=1, max_size=5)
        self.addCleanup(pool_db.close)

        pool_db.execute(f"CREATE SCHEMA {schema}")
        self.addCleanup(lambda: pool_db.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
        pool_db.set_search_path(schema)
        apply_migrations(pool_db)

        # Basic query and execution via pool
        res = pool_db.execute(
            "INSERT INTO audit_events (id, occurred_at, actor, action, subject_type, details) "
            "VALUES ('a1', '2026-11-01T00:00:00Z', 'tester', 'test_action', 'scan', '{}')"
        )
        self.assertEqual(res, 1)

        row = pool_db.query_one("SELECT actor, action FROM audit_events WHERE id = 'a1'")
        self.assertIsNotNone(row)
        self.assertEqual(row["actor"], "tester")

        # Transaction rollback on error
        with self.assertRaises(ValueError), pool_db.transaction():
            pool_db.execute(
                "INSERT INTO audit_events (id, occurred_at, actor, action, subject_type, details) "
                "VALUES ('a2', '2026-11-01T00:00:00Z', 'tester', 'rollback_test', 'scan', '{}')"
            )
            raise ValueError("trigger rollback")

        rolled_back = pool_db.query_one("SELECT * FROM audit_events WHERE id = 'a2'")
        self.assertIsNone(rolled_back)

    def test_postgres_concurrent_threads_in_pool(self):
        schema = f"sbh_threads_{uuid.uuid4().hex[:12]}"
        pool_db = PostgresPoolDatabase(POSTGRES_DSN, min_size=2, max_size=8)
        self.addCleanup(pool_db.close)

        pool_db.execute(f"CREATE SCHEMA {schema}")
        self.addCleanup(lambda: pool_db.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
        pool_db.set_search_path(schema)
        apply_migrations(pool_db)

        def worker(thread_idx: int) -> int:
            pool_db.execute(
                "INSERT INTO audit_events (id, occurred_at, actor, action, subject_type, details) "
                "VALUES (:id, '2026-11-01T00:00:00Z', :actor, 'concurrent_write', 'scan', '{}')",
                {"id": f"t_{thread_idx}", "actor": f"worker_{thread_idx}"},
            )
            return thread_idx

        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            futures = [executor.submit(worker, i) for i in range(12)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        self.assertEqual(len(results), 12)
        count = pool_db.query_one(
            f"SELECT COUNT(*) AS c FROM {schema}.audit_events WHERE action = 'concurrent_write'"
        )
        self.assertEqual(count["c"], 12)


if __name__ == "__main__":
    unittest.main()
