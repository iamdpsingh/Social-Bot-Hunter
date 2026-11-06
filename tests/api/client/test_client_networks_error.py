from __future__ import annotations

from unittest.mock import MagicMock

from services.api.client.networks import NetworksClient


def test_networks_client_empty_scan() -> None:
    session = MagicMock()
    session.get.return_value = {"clusters": [], "total": 0}
    client = NetworksClient(session)
    res = client.get_clusters("empty_scan")
    assert res["total"] == 0
