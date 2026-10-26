"""Neighbourhood Jaccard similarity between accounts."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from itertools import combinations
from typing import Any

import networkx as nx

from sbh.config import GraphLimits
from sbh.graph.build import Deadline
from sbh.shared.errors import GraphLimitExceeded


@dataclass(frozen=True)
class SimilarPair:
    a: str  # a < b lexicographically
    b: str
    jaccard: float
    shared: int  # size of the neighbourhood intersection (excluding the pair itself)


def jaccard(x: set[str], y: set[str]) -> float:
    union = x | y
    return len(x & y) / len(union) if union else 0.0


def neighbour_pairs(
    g: nx.DiGraph, *, direction: str, min_degree: int, min_shared: int, max_posting: int,
    limits: GraphLimits, deadline: Deadline,
) -> tuple[list[SimilarPair], dict[str, Any]]:
    """All account pairs whose neighbourhoods overlap in at least ``min_shared`` accounts.

    ``direction='out'`` compares who accounts *follow* (shared follow targets); ``'in'``
    compares who *follows* them. Candidate pairs come from an inverted index (neighbour ->
    accounts), so work scales with overlap rather than with all N^2 pairs. Neighbours shared
    by more than ``max_posting`` accounts (celebrity-scale hubs) are skipped when *generating*
    candidates and reported in the stats, but they still count in the exact Jaccard.

    Each pair's sets exclude the pair's own two members, so two accounts that follow each other
    do not inflate their own overlap.
    """
    if direction not in ("out", "in"):
        raise ValueError("direction must be 'out' or 'in'")
    neigh: Callable[[str], Any] = g.successors if direction == "out" else g.predecessors
    sets: dict[str, set[str]] = {}
    for n in g.nodes:
        s = set(neigh(n))
        if len(s) >= min_degree:
            sets[n] = s

    posting: dict[str, list[str]] = {}
    for n in sorted(sets):
        for t in sets[n]:
            posting.setdefault(t, []).append(n)

    counts: dict[tuple[str, str], int] = {}
    skipped_hubs = 0
    for i, t in enumerate(sorted(posting)):
        members = posting[t]
        if len(members) < 2:
            continue
        if len(members) > max_posting:
            skipped_hubs += 1
            continue
        if i % 500 == 0:
            deadline.check("similarity candidate generation")
        for pair in combinations(members, 2):
            counts[pair] = counts.get(pair, 0) + 1
        if len(counts) > limits.max_pairs:
            raise GraphLimitExceeded(f"more than {limits.max_pairs} candidate pairs")

    out: list[SimilarPair] = []
    for k, ((a, b), c) in enumerate(sorted(counts.items())):
        if c < min_shared:
            continue
        if k % 2000 == 0:
            deadline.check("similarity scoring")
        sa, sb = sets[a] - {b}, sets[b] - {a}
        inter = len(sa & sb)
        if inter < min_shared:
            continue
        union = len(sa | sb)
        out.append(SimilarPair(a, b, inter / union if union else 0.0, inter))
    return out, {"skipped_hub_targets": skipped_hubs, "candidate_pairs": len(counts),
                 "accounts_compared": len(sets)}
