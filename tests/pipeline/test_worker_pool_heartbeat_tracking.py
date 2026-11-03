from __future__ import annotations

import time
import unittest

from sbh.pipeline.worker import WorkerPool
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations


class PipelineWorkerTest_test_worker_pool_heartbeat_tracking(unittest.TestCase):
    def test_heartbeats(self) -> None:
        db = SQLiteDatabase(":memory:")
        apply_migrations(db)
        pool = WorkerPool(db, worker_count=1)
        pool.start()
        time.sleep(0.1)
        self.assertGreater(len(pool._heartbeats), 0)
        pool.stop(timeout=1.0)
