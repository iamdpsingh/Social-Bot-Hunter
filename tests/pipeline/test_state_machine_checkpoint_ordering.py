from __future__ import annotations
import unittest
from datetime import datetime, timezone
from sbh.pipeline.state import CheckpointRecord, ScanStage, ScanStateMachine
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository

class PipelineStateTest_test_state_machine_checkpoint_ordering(unittest.TestCase):
    def test_ordering(self) -> None:
        db = SQLiteDatabase(':memory:')
        apply_migrations(db)
        repo = ScanRepository(db)
        scan_id = repo.create_scan(
            scan_type='api_collection', collection_mode='official_api', platform='x',
            data_origin='api', requested_by='test', reference_time=datetime.now(timezone.utc),
            config_version='1.0', config_sha256='sha'
        )
        sm = ScanStateMachine(db, scan_id)
        sm.record_checkpoint(CheckpointRecord(scan_id=scan_id, stage=ScanStage.VALIDATE, processed_count=10))
        sm.record_checkpoint(CheckpointRecord(scan_id=scan_id, stage=ScanStage.EXTRACT_FEATURES, processed_count=20))
        latest = sm.get_latest_checkpoint()
        assert latest is not None
        self.assertEqual(latest['stage'], 'extract_features')
