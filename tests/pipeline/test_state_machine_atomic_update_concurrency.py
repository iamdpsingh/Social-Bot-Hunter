from __future__ import annotations
import unittest
from datetime import datetime, timezone
from sbh.pipeline.state import ScanStateMachine, ScanStatus
from sbh.shared.errors import InvalidTransitionError
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository

class PipelineStateTest_test_state_machine_atomic_update_concurrency(unittest.TestCase):
    def test_wrong_source_rejected(self) -> None:
        db = SQLiteDatabase(':memory:')
        apply_migrations(db)
        repo = ScanRepository(db)
        scan_id = repo.create_scan(
            scan_type='api_collection', collection_mode='official_api', platform='x',
            data_origin='api', requested_by='test', reference_time=datetime.now(timezone.utc),
            config_version='1.0', config_sha256='sha'
        )
        sm = ScanStateMachine(db, scan_id)
        # Attempt illegal direct jump from pending to complete
        with self.assertRaises(InvalidTransitionError):
            sm.transition(ScanStatus.COMPLETED)
