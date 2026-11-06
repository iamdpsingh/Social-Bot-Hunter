"""Networks and graph API client SDK module."""

from __future__ import annotations

from typing import Any

from services.api.client.session import ApiSession


class NetworksClient:
    """Client for network graphs, clusters, and ego-neighborhood endpoints."""

    def __init__(self, session: ApiSession) -> None:
        self.session = session

    def get_clusters(self, scan_id: str) -> dict[str, Any]:
        """Retrieve coordinated bot clusters for a scan."""
        return self.session.get(f"/scans/{scan_id}/networks/clusters")

    def get_graph(
        self,
        scan_id: str,
        max_nodes: int = 500,
        cluster_id: str | None = None,
        risk_band: str | None = None,
        min_score: float | None = None,
    ) -> dict[str, Any]:
        """Retrieve Cytoscape.js formatted elements with optional filters."""
        params: dict[str, Any] = {"max_nodes": max_nodes}
        if cluster_id:
            params["cluster_id"] = cluster_id
        if risk_band:
            params["risk_band"] = risk_band
        if min_score is not None:
            params["min_score"] = min_score
        return self.session.get(f"/scans/{scan_id}/networks/graph", params=params)

    def get_node_neighbors(
        self,
        scan_id: str,
        node_id: str,
        direction: str = "both",
        radius: int = 1,
    ) -> dict[str, Any]:
        """Expand ego-network neighbors for a focal node."""
        params = {"direction": direction, "radius": radius}
        return self.session.get(f"/scans/{scan_id}/networks/nodes/{node_id}/neighbors", params=params)

    def get_metrics(self, scan_id: str) -> dict[str, Any]:
        """Retrieve macroscopic topology metrics for the scan network."""
        return self.session.get(f"/scans/{scan_id}/networks/metrics")

    def export_graph(self, scan_id: str, format: str = "cytoscape_json") -> dict[str, Any]:
        """Export network elements and summary bundle."""
        return self.session.get(f"/scans/{scan_id}/networks/export", params={"format": format})
