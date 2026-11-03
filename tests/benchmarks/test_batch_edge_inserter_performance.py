from __future__ import annotations

import unittest
from datetime import UTC, datetime

from sbh.storage.batch import BatchEdgeInserter
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository


class BenchmarkTest_test_batch_edge_inserter_performance(unittest.TestCase):
    def test_high_throughput(self) -> None:
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
        db.execute(
            "INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance) VALUES ('src', 'x', 'user_src', '2026-01-01', '2026-01-01', '{}', 'api')"
        )
        for i in range(100):
            db.execute(
                "INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance) VALUES (:id, 'x', :p, '2026-01-01', '2026-01-01', '{}', 'api')",
                {"id": f"dst_{i}", "p": f"p_{i}"},
            )
        edges = [
            {
                "id": f"e_{i}",
                "scan_id": scan_id,
                "platform": "x",
                "source_account_id": "src",
                "target_account_id": f"dst_{i % 100}",
                "relationship_type": "follows",
                "observed_at": "2026-01-01T00:00:00Z",
                "collected_at": "2026-01-01T00:00:00Z",
                "verification_status": "source_asserted",
                "provenance": "api",
            }
            for i in range(500)
        ]
        inserter = BatchEdgeInserter(db, chunk_size=250)
        stats = inserter.insert_edges_chunked(scan_id, edges)
        self.assertEqual(stats.total_records, 500)
        self.assertGreater(stats.throughput_records_per_sec, 500.0)
