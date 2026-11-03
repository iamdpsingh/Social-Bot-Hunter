from __future__ import annotations

import unittest

from sbh.pipeline.worker import WorkerPool
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations


class PipelineWorkerTest_test_worker_pool_is_running_check(unittest.TestCase):
    def test_is_running(self) -> None:
        db = SQLiteDatabase(":memory:")
        apply_migrations(db)
        pool = WorkerPool(db, worker_count=1)
        self.assertFalse(pool.is_running())
        pool.start()
        self.assertTrue(pool.is_running())
        pool.stop(timeout=1.0)
        self.assertFalse(pool.is_running())
