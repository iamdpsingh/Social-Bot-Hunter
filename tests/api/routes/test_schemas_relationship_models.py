from __future__ import annotations

from services.api.schemas import (
    AccountExportBundleResponse,
    RelationshipItem,
    RelationshipListResponse,
)


def test_relationship_schemas_validation() -> None:
    item = RelationshipItem(
        source_account_id="user_a",
        target_account_id="user_b",
        relationship_type="follower",
    )
    assert item.source_account_id == "user_a"

    res = RelationshipListResponse(
        scan_id="scan_10",
        total=1,
        offset=0,
        limit=50,
        relationships=[item],
    )
    assert res.total == 1
    assert len(res.relationships) == 1

def test_export_bundle_schema_validation() -> None:
    bundle = AccountExportBundleResponse(
        scan={"id": "scan_1"},
        exported_at="2026-11-05T09:00:00Z",
        is_synthetic=False,
        total_accounts=0,
        accounts=[],
        clusters=[],
    )
    assert bundle.total_accounts == 0
