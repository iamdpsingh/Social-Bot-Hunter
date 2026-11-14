"""Cytoscape.js JSON schema and structural topology validator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CytoscapeElementReport:
    """Report detailing validity of a Cytoscape.js export."""

    is_valid: bool
    node_count: int
    edge_count: int
    orphan_edges: list[str] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)
    risk_distribution: dict[str, int] = field(default_factory=dict)
    cluster_counts: dict[str, int] = field(default_factory=dict)


class CytoscapeValidator:
    """Validates that graph serialization conforms to Cytoscape.js and frontend specs."""

    REQUIRED_NODE_KEYS = ("id", "label")
    REQUIRED_EDGE_KEYS = ("id", "source", "target")

    @classmethod
    def validate(cls, elements: dict[str, list[dict[str, Any]]]) -> CytoscapeElementReport:
        """Validate Cytoscape element dictionary."""
        missing: list[str] = []
        orphan_edges: list[str] = []
        risk_dist: dict[str, int] = {"bot": 0, "suspicious": 0, "human": 0, "unknown": 0}
        cluster_counts: dict[str, int] = {}

        if not isinstance(elements, dict):
            return CytoscapeElementReport(is_valid=False, node_count=0, edge_count=0, missing_fields=["elements_not_dict"])

        nodes_list = elements.get("nodes", [])
        edges_list = elements.get("edges", [])

        node_ids: set[str] = set()

        for idx, node_item in enumerate(nodes_list):
            if not isinstance(node_item, dict) or "data" not in node_item:
                missing.append(f"node[{idx}].data")
                continue
            data = node_item["data"]
            for req in cls.REQUIRED_NODE_KEYS:
                if req not in data:
                    missing.append(f"node[{idx}].data.{req}")
            nid = str(data.get("id", ""))
            node_ids.add(nid)

            risk_class = data.get("risk_category", "unknown")
            risk_dist[risk_class] = risk_dist.get(risk_class, 0) + 1

            cid = data.get("cluster_id")
            if cid:
                cluster_counts[str(cid)] = cluster_counts.get(str(cid), 0) + 1

        for idx, edge_item in enumerate(edges_list):
            if not isinstance(edge_item, dict) or "data" not in edge_item:
                missing.append(f"edge[{idx}].data")
                continue
            data = edge_item["data"]
            for req in cls.REQUIRED_EDGE_KEYS:
                if req not in data:
                    missing.append(f"edge[{idx}].data.{req}")
            src = str(data.get("source", ""))
            dst = str(data.get("target", ""))
            if src not in node_ids or dst not in node_ids:
                orphan_edges.append(f"{src}->{dst}")

        is_valid = len(missing) == 0 and len(orphan_edges) == 0

        return CytoscapeElementReport(
            is_valid=is_valid,
            node_count=len(nodes_list),
            edge_count=len(edges_list),
            orphan_edges=orphan_edges,
            missing_fields=missing,
            risk_distribution=risk_dist,
            cluster_counts=cluster_counts,
        )
