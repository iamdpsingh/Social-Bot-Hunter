"""Graph construction with hard resource limits and strict platform separation."""

from __future__ import annotations

import time
from collections.abc import Callable, Iterable

import networkx as nx

from sbh.config import GraphLimits
from sbh.shared.errors import GraphLimitExceeded


class Deadline:
    """Wall-clock budget for a graph stage. ``check`` raises instead of letting work run on."""

    def __init__(self, max_seconds: float, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self._end = clock() + max_seconds
        self.max_seconds = max_seconds

    def check(self, what: str) -> None:
        if self._clock() > self._end:
            raise GraphLimitExceeded(f"runtime limit of {self.max_seconds}s exceeded during {what}")


def build_graph(platform: str, edges: Iterable[tuple[str, str]], limits: GraphLimits,
                extra_nodes: Iterable[str] = ()) -> nx.DiGraph:
    """Build one directed graph for one platform. ``(a, b)`` means *a follows b*; the reverse edge
    is never added. Exceeding a limit raises ``GraphLimitExceeded``; nothing is truncated silently."""
    g: nx.DiGraph = nx.DiGraph(platform=platform)
    count = 0
    for src, dst in edges:
        count += 1
        if count > limits.max_edges:
            raise GraphLimitExceeded(f"more than {limits.max_edges} edges")
        g.add_edge(src, dst)
        if g.number_of_nodes() > limits.max_nodes:
            raise GraphLimitExceeded(f"more than {limits.max_nodes} nodes")
    g.add_nodes_from(extra_nodes)
    if g.number_of_nodes() > limits.max_nodes:
        raise GraphLimitExceeded(f"more than {limits.max_nodes} nodes")
    return g


def graphs_by_platform(triples: Iterable[tuple[str, str, str]], limits: GraphLimits) -> dict[str, nx.DiGraph]:
    """Split ``(platform, source, target)`` triples into separate graphs.

    The same identifier on two platforms is two different accounts: identity namespaces never
    merge, and usernames are never used to link accounts across platforms.
    """
    grouped: dict[str, list[tuple[str, str]]] = {}
    for platform, src, dst in triples:
        grouped.setdefault(platform, []).append((src, dst))
    return {p: build_graph(p, e, limits) for p, e in sorted(grouped.items())}
