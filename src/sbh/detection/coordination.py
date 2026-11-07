"""Coordinated activity detection aggregating text, temporal, and graph signals.

Detects synchronized campaigns across accounts by correlating:
1. SimHash content clusters (identical or templated messages)
2. Temporal synchronisation bursts (statistically abnormal co-posting)
3. Shared follower/following hubs (graph neighborhood overlap)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import networkx as nx

from sbh.detection.simhash import SimHashCluster, cluster_texts
from sbh.graph.temporal import sync_lift


@dataclass(frozen=True)
class TemporalBurstWindow:
    """A detected burst of synchronized postings across coordinated accounts."""

    burst_id: str
    start_timestamp: float
    end_timestamp: float
    post_count: int
    participating_accounts: list[str]
    coordination_lift: float


@dataclass(frozen=True)
class SharedTargetHub:
    """A shared destination account followed or targeted by multiple coordinated bots."""

    target_id: str
    target_handle: str
    shared_by_count: int
    follower_account_ids: list[str]
    jaccard_overlap: float


@dataclass(frozen=True)
class CoordinationAnalysis:
    """Composite analysis of coordinated activity for an investigation scan."""

    scan_id: str
    simhash_clusters: list[SimHashCluster]
    temporal_bursts: list[TemporalBurstWindow]
    shared_hubs: list[SharedTargetHub]
    total_coordinated_accounts: int
    overall_coordination_score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "scan_id": self.scan_id,
            "simhash_clusters": [
                {
                    "cluster_id": c.cluster_id,
                    "representative_text": c.representative_text,
                    "member_count": c.member_count,
                    "account_ids": c.account_ids,
                    "sample_texts": c.sample_texts,
                    "avg_pairwise_similarity": c.avg_pairwise_similarity,
                    "max_hamming_distance": c.max_hamming_distance,
                }
                for c in self.simhash_clusters
            ],
            "temporal_bursts": [
                {
                    "burst_id": b.burst_id,
                    "start_timestamp": b.start_timestamp,
                    "end_timestamp": b.end_timestamp,
                    "post_count": b.post_count,
                    "participating_accounts": b.participating_accounts,
                    "coordination_lift": b.coordination_lift,
                }
                for b in self.temporal_bursts
            ],
            "shared_hubs": [
                {
                    "target_id": h.target_id,
                    "target_handle": h.target_handle,
                    "shared_by_count": h.shared_by_count,
                    "follower_account_ids": h.follower_account_ids,
                    "jaccard_overlap": h.jaccard_overlap,
                }
                for h in self.shared_hubs
            ],
            "total_coordinated_accounts": self.total_coordinated_accounts,
            "overall_coordination_score": self.overall_coordination_score,
        }


def detect_coordination(
    scan_id: str,
    messages: list[dict[str, Any]],
    posts_by_account: dict[str, list[float]],
    graph: nx.DiGraph | None = None,
    burst_window_seconds: float = 60.0,
    min_similarity_distance: int = 4,
) -> CoordinationAnalysis:
    """Execute complete coordination detection pipeline over an investigation scan."""
    # 1. SimHash content clustering
    sim_clusters = cluster_texts(messages, max_hamming_distance=min_similarity_distance)

    # 2. Temporal synchronisation detection
    bursts: list[TemporalBurstWindow] = []
    sync_res = sync_lift(posts_by_account, window=burst_window_seconds, min_posts=2)
    lift_val = sync_res.lift if sync_res.lift is not None else 1.0

    all_posts: list[tuple[float, str]] = []
    for acc, timestamps in posts_by_account.items():
        for ts in timestamps:
            all_posts.append((ts, acc))
    all_posts.sort()

    if all_posts:
        burst_idx = 1
        current_burst: list[tuple[float, str]] = [all_posts[0]]
        for ts, acc in all_posts[1:]:
            if ts - current_burst[-1][0] <= burst_window_seconds:
                current_burst.append((ts, acc))
            else:
                accs = list({p[1] for p in current_burst})
                if len(accs) >= 2 and len(current_burst) >= 3:
                    bursts.append(
                        TemporalBurstWindow(
                            burst_id=f"burst_{burst_idx:03d}",
                            start_timestamp=current_burst[0][0],
                            end_timestamp=current_burst[-1][0],
                            post_count=len(current_burst),
                            participating_accounts=accs,
                            coordination_lift=round(lift_val, 2),
                        )
                    )
                    burst_idx += 1
                current_burst = [(ts, acc)]
        accs = list({p[1] for p in current_burst})
        if len(accs) >= 2 and len(current_burst) >= 3:
            bursts.append(
                TemporalBurstWindow(
                    burst_id=f"burst_{burst_idx:03d}",
                    start_timestamp=current_burst[0][0],
                    end_timestamp=current_burst[-1][0],
                    post_count=len(current_burst),
                    participating_accounts=accs,
                    coordination_lift=round(lift_val, 2),
                )
            )

    # 3. Shared follow hubs
    shared_hubs: list[SharedTargetHub] = []
    if graph is not None and graph.number_of_nodes() > 0:
        in_counts: dict[str, list[str]] = {}
        for u, v in graph.edges():
            in_counts.setdefault(v, []).append(u)

        for target, followers in in_counts.items():
            if len(followers) >= 2:
                # Compute average jaccard overlap
                target_handle = graph.nodes[target].get("handle", target) if target in graph.nodes else target
                shared_hubs.append(
                    SharedTargetHub(
                        target_id=target,
                        target_handle=target_handle,
                        shared_by_count=len(followers),
                        follower_account_ids=followers,
                        jaccard_overlap=round(min(1.0, len(followers) / max(1, graph.number_of_nodes())), 4),
                    )
                )
        shared_hubs.sort(key=lambda x: x.shared_by_count, reverse=True)

    # Composite account tally & coordination score
    coordinated_accs: set[str] = set()
    for c in sim_clusters:
        coordinated_accs.update(c.account_ids)
    for b in bursts:
        coordinated_accs.update(b.participating_accounts)
    for h in shared_hubs[:10]:
        coordinated_accs.update(h.follower_account_ids)

    score_text = min(1.0, len(sim_clusters) * 0.25)
    score_temp = min(1.0, len(bursts) * 0.20 + (0.3 if lift_val > 1.5 else 0.0))
    score_graph = min(1.0, len(shared_hubs) * 0.15)
    overall_score = round(float(score_text * 0.45 + score_temp * 0.35 + score_graph * 0.20), 4)

    return CoordinationAnalysis(
        scan_id=scan_id,
        simhash_clusters=sim_clusters,
        temporal_bursts=bursts,
        shared_hubs=shared_hubs[:20],
        total_coordinated_accounts=len(coordinated_accs),
        overall_coordination_score=overall_score,
    )
