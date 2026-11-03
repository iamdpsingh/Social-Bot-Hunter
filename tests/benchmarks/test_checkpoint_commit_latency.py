from __future__ import annotations

import time
import unittest
from datetime import UTC, datetime

from sbh.pipeline.state import CheckpointRecord, ScanStage, ScanStateMachine
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository


class BenchmarkTest_test_checkpoint_commit_latency(unittest.TestCase):
    def test_checkpoint_perf(self) -> None:
        db = SQLiteDatabase(":memory:")
        apply_migrations(db)
        repo = ScanRepository(db)
        scan_id = repo.create_scan(
            scan_type="api_collection",
            collection_mode="official_api",
            platform="x",
            data_origin="api",
            requested_by="bench",
            reference_time=datetime.now(UTC),
            config_version="1.0",
            config_sha256="sha",
        )
        sm = ScanStateMachine(db, scan_id)
        t0 = time.perf_counter()
        for s in list(ScanStage)[:5]:
            sm.record_checkpoint(CheckpointRecord(scan_id=scan_id, stage=s, processed_count=100))
        duration = time.perf_counter() - t0
        self.assertLess(duration, 0.5)
