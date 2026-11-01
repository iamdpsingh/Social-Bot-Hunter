from __future__ import annotations

from tests.support import DbTestCase


class StorageReportsJsonSchemaTestCase(DbTestCase):
    def test_evidence_records_storage(self) -> None:
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time, status_detail)
            VALUES ('s_ev', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}')""")
        self.db.execute("""INSERT INTO model_versions (id, kind, name, version, config, config_sha256, created_at)
            VALUES ('mv_ev', 'rules', 'heuristics', '1.0', '{}', 'sha_ev', '2026-10-01T00:00:00Z')""")
        self.db.execute("""INSERT INTO evidence_records (id, scan_id, subject_type, subject_id, evidence_type, summary, details, source_refs, model_version_id, created_at)
            VALUES ('ev_1', 's_ev', 'account', 'acc_1', 'burst', 'Simultaneous burst', '{}', '[]', 'mv_ev', '2026-10-01T00:00:00Z')""")
        row = self.db.query_one("SELECT evidence_type FROM evidence_records WHERE id = 'ev_1'")
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["evidence_type"], "burst")
