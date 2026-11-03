from __future__ import annotations

from tests.support import DbTestCase


class StorageRiskBandSortingTestCase(DbTestCase):
    def test_risk_assessment_sorting(self) -> None:
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time, status_detail)
            VALUES ('s_rb', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}')""")
        self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
            VALUES ('a_r1', 'x', 'r1', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')""")
        self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
            VALUES ('a_r2', 'x', 'r2', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')""")
        self.db.execute("""INSERT INTO model_versions (id, kind, name, version, config, config_sha256, created_at)
            VALUES ('mv_r', 'rules', 'heuristics', '1.0', '{}', 'sha_r', '2026-10-01T00:00:00Z')""")
        self.db.execute("""INSERT INTO risk_assessments (id, scan_id, platform_account_id, feature_version, model_version_id, status, score, band, evidence_coverage, features_available, features_total, contributions, limitations, assessed_at)
            VALUES ('ra_1', 's_rb', 'a_r1', 'v1', 'mv_r', 'scored', 85.0, 'high', 1.0, 10, 10, '{}', '[]', '2026-10-01T00:00:00Z')""")
        self.db.execute("""INSERT INTO risk_assessments (id, scan_id, platform_account_id, feature_version, model_version_id, status, score, band, evidence_coverage, features_available, features_total, contributions, limitations, assessed_at)
            VALUES ('ra_2', 's_rb', 'a_r2', 'v1', 'mv_r', 'scored', 20.0, 'low', 1.0, 10, 10, '{}', '[]', '2026-10-01T00:00:00Z')""")
        rows = self.db.query_all(
            "SELECT score FROM risk_assessments WHERE scan_id = 's_rb' ORDER BY score DESC"
        )
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["score"], 85.0)
        self.assertEqual(rows[1]["score"], 20.0)
