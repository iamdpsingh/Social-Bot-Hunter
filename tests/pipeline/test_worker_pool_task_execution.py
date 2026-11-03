from __future__ import annotations
import time
import unittest
from datetime import datetime, timezone
from sbh.pipeline.worker import WorkerPool
from sbh.pipeline.state import ScanStatus
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository

class PipelineWorkerTest_test_worker_pool_task_execution(unittest.TestCase):
    def test_task_executes(self) -> None:
        db = SQLiteDatabase(':memory:')
        apply_migrations(db)
        repo = ScanRepository(db)
        scan_id = repo.create_scan(
            scan_type='api_collection', collection_mode='official_api', platform='x',
            data_origin='api', requested_by='test', reference_time=datetime.now(timezone.utc),
            config_version='1.0', config_sha256='sha'
        )
        pool = WorkerPool(db, worker_count=1)
        pool.start()
        pool.submit_scan(scan_id)
        time.sleep(0.3)
        pool.stop(timeout=1.0)
        scan = repo.get_scan(scan_id)
        self.assertIsNotNone(scan)
        assert scan is not None
        self.assertEqual(scan['status'], ScanStatus.COMPLETED.value)
