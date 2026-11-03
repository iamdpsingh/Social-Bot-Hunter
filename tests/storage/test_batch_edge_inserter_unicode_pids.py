from __future__ import annotations
import unittest
from datetime import datetime, timezone
from sbh.storage.batch import BatchEdgeInserter
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository

class StorageBatchTest_test_batch_edge_inserter_unicode_pids(unittest.TestCase):
    def test_unicode_edge(self) -> None:
        db = SQLiteDatabase(':memory:')
        apply_migrations(db)
        repo = ScanRepository(db)
        scan_id = repo.create_scan(
            scan_type='api_collection', collection_mode='official_api', platform='x',
            data_origin='api', requested_by='test', reference_time=datetime.now(timezone.utc),
            config_version='1.0', config_sha256='sha'
        )
        db.execute("INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at) VALUES ('acc_u1', 'x', 'üser_ñame', '2026-01-01', '2026-01-01')")
        db.execute("INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at) VALUES ('acc_u2', 'x', 'bot_🚀', '2026-01-01', '2026-01-01')")
        edge = {
            'id': 'e_u', 'scan_id': scan_id, 'platform': 'x', 'source_account_id': 'acc_u1',
            'target_account_id': 'acc_u2', 'relationship_type': 'follows', 'observed_at': '2026-01-01T00:00:00Z',
            'collected_at': '2026-01-01T00:00:00Z', 'verification_status': 'observed', 'provenance': 'api'
        }
        inserter = BatchEdgeInserter(db, chunk_size=100)
        stats = inserter.insert_edges_chunked(scan_id, [edge])
        self.assertEqual(stats.total_records, 1)
