from __future__ import annotations
import threading
import time
import unittest
from datetime import datetime, timezone
from sbh.pipeline.worker import WorkerPool
from sbh.pipeline.state import ScanStatus
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository

class PipelineWorkerTest_test_worker_pool_custom_runner(unittest.TestCase):
    def test_custom_runner_invoked(self) -> None:
        db = SQLiteDatabase(':memory:')
        apply_migrations(db)
        repo = ScanRepository(db)
        scan_id = repo.create_scan(
            scan_type='api_collection', collection_mode='official_api', platform='x',
            data_origin='api', requested_by='test', reference_time=datetime.now(timezone.utc),
            config_version='1.0', config_sha256='sha'
        )
        executed = []
        def my_runner(sid: str, params: dict, cancel_tok: threading.Event) -> None:
            executed.append(sid)

        pool = WorkerPool(db, worker_count=1, runner_fn=my_runner)
        pool.start()
        pool.submit_scan(scan_id)
        time.sleep(0.3)
        pool.stop(timeout=1.0)
        self.assertIn(scan_id, executed)
        scan = repo.get_scan(scan_id)
        assert scan is not None
        self.assertEqual(scan['status'], ScanStatus.COMPLETED.value)
