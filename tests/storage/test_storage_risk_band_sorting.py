from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageRiskBandSortingTestCase(DbTestCase):
    def test_risk_assessment_sorting(self):
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time)
            VALUES ('s_rb', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z')""")
        self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
            VALUES ('a_r1', 'x', 'r1', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')""")
        self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
            VALUES ('a_r2', 'x', 'r2', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')""")
        self.db.execute("""INSERT INTO risk_assessments (id, platform_account_id, scan_id, evaluated_at, risk_score, risk_band, confidence, reasons)
            VALUES ('ra_1', 'a_r1', 's_rb', '2026-10-01T00:00:00Z', 85, 'high', 0.9, '[]')""")
        self.db.execute("""INSERT INTO risk_assessments (id, platform_account_id, scan_id, evaluated_at, risk_score, risk_band, confidence, reasons)
            VALUES ('ra_2', 'a_r2', 's_rb', '2026-10-01T00:00:00Z', 20, 'low', 0.8, '[]')""")
        rows = self.db.query("SELECT risk_score FROM risk_assessments WHERE scan_id = 's_rb' ORDER BY risk_score DESC")
        self.assertEqual(rows[0]["risk_score"], 85)
        self.assertEqual(rows[1]["risk_score"], 20)
