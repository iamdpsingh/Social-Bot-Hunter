from __future__ import annotations

import unittest
from datetime import UTC, datetime

from sbh.storage.batch import BatchEdgeInserter
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository


class StorageBatchTest_test_batch_edge_inserter_multi_chunk(unittest.TestCase):
    def test_multi_chunk(self) -> None:
        db = SQLiteDatabase(":memory:")
        apply_migrations(db)
        repo = ScanRepository(db)
        scan_id = repo.create_scan(
            scan_type="api_collection",
            collection_mode="official_api",
            platform="x",
            data_origin="api",
            requested_by="test",
            reference_time=datetime.now(UTC),
            config_version="1.0",
            config_sha256="sha",
        )
        for i in range(10):
            db.execute(
                "INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance) VALUES (:id, 'x', :p, '2026-01-01', '2026-01-01', '{}', 'api')",
                {"id": f"acc_{i}", "p": f"user_{i}"},
            )
        edges = [
            {
                "id": f"e_{i}",
                "scan_id": scan_id,
                "platform": "x",
                "source_account_id": "acc_0",
                "target_account_id": f"acc_{i}",
                "relationship_type": "follows",
                "observed_at": "2026-01-01T00:00:00Z",
                "collected_at": "2026-01-01T00:00:00Z",
                "verification_status": "source_asserted",
                "provenance": "api",
            }
            for i in range(1, 10)
        ]
        inserter = BatchEdgeInserter(db, chunk_size=3)
        stats = inserter.insert_edges_chunked(scan_id, edges)
        self.assertEqual(stats.total_records, 9)
        self.assertEqual(stats.chunks_executed, 3)
