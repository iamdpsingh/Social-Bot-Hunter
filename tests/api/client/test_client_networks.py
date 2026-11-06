from __future__ import annotations

from unittest.mock import MagicMock

from services.api.client.networks import NetworksClient


def test_networks_client_methods() -> None:
    session = MagicMock()
    session.get.return_value = {"ok": True}
    client = NetworksClient(session)

    client.get_clusters("scan_1")
    session.get.assert_called_with("/scans/scan_1/networks/clusters")

    client.get_graph("scan_1", max_nodes=200, risk_band="critical")
    session.get.assert_called_with(
        "/scans/scan_1/networks/graph",
        params={"max_nodes": 200, "risk_band": "critical"},
    )

    client.get_node_neighbors("scan_1", "acc_99", direction="in")
    session.get.assert_called_with(
        "/scans/scan_1/networks/nodes/acc_99/neighbors",
        params={"direction": "in", "radius": 1},
    )

    client.get_metrics("scan_1")
    session.get.assert_called_with("/scans/scan_1/networks/metrics")

    client.export_graph("scan_1")
    session.get.assert_called_with(
        "/scans/scan_1/networks/export",
        params={"format": "cytoscape_json"},
    )
