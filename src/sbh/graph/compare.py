"""Compare the relationship snapshots of two scans without mistaking missing data for change."""

from __future__ import annotations

from dataclasses import dataclass, field

Edge = tuple[str, str]
Coverage = dict[tuple[str, str], str]  # (account id, 'followers'|'following') -> completeness


@dataclass
class ScanDiff:
    unchanged: set[Edge] = field(default_factory=set)
    confirmed_added: set[Edge] = field(default_factory=set)
    newly_observed: set[Edge] = field(default_factory=set)  # absent earlier, but earlier lists incomplete
    confirmed_removed: set[Edge] = field(default_factory=set)
    not_reobserved: set[Edge] = field(default_factory=set)  # absent now, but current lists incomplete

    def summary(self) -> dict[str, int]:
        return {k: len(getattr(self, k)) for k in
                ("unchanged", "confirmed_added", "newly_observed", "confirmed_removed", "not_reobserved")}


def _list_complete(cov: Coverage, edge: Edge) -> bool:
    """An absence is *proven* if either list that would contain the edge was fully collected."""
    src, dst = edge
    return cov.get((src, "following")) == "complete" or cov.get((dst, "followers")) == "complete"


def diff_edge_sets(earlier: set[Edge], later: set[Edge], earlier_cov: Coverage, later_cov: Coverage) -> ScanDiff:
    """Classify edge changes between two scans.

    A removal is *confirmed* only when the later scan collected a complete list that should have
    contained the edge. An addition is *confirmed* only when the earlier scan collected such a
    list. Otherwise the difference may just reflect different collection coverage and is
    reported separately so it is never presented as a real change in the network.
    """
    d = ScanDiff()
    d.unchanged = earlier & later
    for e in later - earlier:
        (d.confirmed_added if _list_complete(earlier_cov, e) else d.newly_observed).add(e)
    for e in earlier - later:
        (d.confirmed_removed if _list_complete(later_cov, e) else d.not_reobserved).add(e)
    return d
