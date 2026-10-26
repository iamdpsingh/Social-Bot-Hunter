"""Backend-agnostic pipeline run against a real PostgreSQL server.

SKIPPED unless SBH_TEST_POSTGRES_DSN is set (the build environment had no PostgreSQL, so this has
never been executed). Point it at a disposable database: it creates and drops a throw-away schema.
Until this passes, PostgreSQL support is unverified (see docs/status.md).
"""

import unittest

from sbh.config import load_config
from sbh.pipeline.run import import_dataset
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


if __name__ == "__main__":
    unittest.main()
