from __future__ import annotations
import unittest
from sbh.pipeline.worker import WorkerPool
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations

class PipelineWorkerTest_test_worker_pool_start_and_stop(unittest.TestCase):
    def test_pool_lifecycle(self) -> None:
        db = SQLiteDatabase(':memory:')
        apply_migrations(db)
        pool = WorkerPool(db, worker_count=2)
        pool.start()
        self.assertTrue(pool.is_running())
        pool.stop(timeout=1.0)
        self.assertFalse(pool.is_running())
