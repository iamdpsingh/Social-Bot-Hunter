"""Graph network schemas."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel


class GraphNode(BaseModel):
    """Network node payload."""
    id: str
    label: str
    platform: str
    risk_score: float | None = None


class GraphEdge(BaseModel):
    """Network edge payload."""
    source: str
    target: str
    type: str = "follows"


class NetworkGraphResponse(BaseModel):
    """Full graph structure response."""
    scan_id: str
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    density: float
