"""Community detection on the follow graph (context for clusters, never proof on its own)."""

from __future__ import annotations

import networkx as nx


def detect_communities(g: nx.DiGraph, seed: int) -> list[frozenset[str]]:
    """Louvain communities on the undirected projection, deterministic for a fixed seed.

    A dense community is *not* evidence of a bot network: friend groups, fandoms and
    professional communities form dense clusters naturally.
    """
    if g.number_of_nodes() == 0:
        return []
    u = g.to_undirected()
    comms = nx.community.louvain_communities(u, seed=seed)
    return sorted((frozenset(c) for c in comms), key=lambda c: (-len(c), min(c)))


def node_community_index(comms: list[frozenset[str]]) -> dict[str, int]:
    return {n: i for i, c in enumerate(comms) for n in c}
