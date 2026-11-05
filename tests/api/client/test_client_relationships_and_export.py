from __future__ import annotations

from services.api.client.scans import ScansClient


def test_scans_client_methods_signature() -> None:
    assert hasattr(ScansClient, "get_relationships")
    assert hasattr(ScansClient, "export_csv")
    assert hasattr(ScansClient, "export_json")
