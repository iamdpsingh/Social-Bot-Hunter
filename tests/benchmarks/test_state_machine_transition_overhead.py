from __future__ import annotations

import time
import unittest
from datetime import UTC, datetime

from sbh.pipeline.state import ScanStateMachine, ScanStatus
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository


class BenchmarkTest_test_state_machine_transition_overhead(unittest.TestCase):
    def test_transition_overhead(self) -> None:
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
        sm.transition(ScanStatus.RUNNING)
        sm.transition(ScanStatus.COMPLETED)
        duration = time.perf_counter() - t0
        self.assertLess(duration, 0.2)
