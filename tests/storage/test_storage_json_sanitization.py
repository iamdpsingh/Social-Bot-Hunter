from __future__ import annotations

from tests.support import DbTestCase


class StorageJsonSanitizationTestCase(DbTestCase):
    def test_metadata_handles_nested_objects(self) -> None:
        self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
            VALUES ('a_json', 'x', 'j1', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{"tags": ["bot", "spammer"], "flagged": true}', 'test')""")
        row = self.db.query_one("SELECT metadata FROM platform_accounts WHERE id = 'a_json'")
        self.assertIsNotNone(row)
        assert row is not None
        self.assertIn("flagged", str(row["metadata"]))
