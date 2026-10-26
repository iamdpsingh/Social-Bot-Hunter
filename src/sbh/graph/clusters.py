"""Candidate coordinated-network detection.

Method ``similarity-louvain`` (version 1):

1. Keep account pairs whose *followed-account* sets overlap strongly (Jaccard threshold, a
   minimum number of shared targets, a minimum out-degree).
2. Group those accounts with seeded Louvain on the similarity graph.
3. For every group of acceptable size, gather independent evidence: structure, shared targets,
   repeated content across members, timing synchronisation, member risk scores.
4. Record coverage, uncertainty and the *alternative explanations* that remain possible.

Structural similarity alone only ever yields ``signal_strength = low``: friend groups, fandoms
and professional communities overlap heavily too. Strength rises only with independent
behavioural evidence, and confidence never exceeds ``moderate`` from automation alone.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field
from itertools import combinations
from typing import Any

import networkx as nx

from sbh.config import GraphConfig
from sbh.graph.build import Deadline
from sbh.graph.metrics import in_degree_threshold
from sbh.graph.similarity import SimilarPair
from sbh.graph.temporal import sync_lift
from sbh.ingestion.fingerprint import duplicate_components
from sbh.shared.models import Post

METHOD = "similarity-louvain"
METHOD_VERSION = "1"
_MAX_POSTS_FOR_CONTENT = 200_000


@dataclass
class ClusterCandidate:
    members: list[str]
    member_metrics: dict[str, dict[str, Any]]
    metrics: dict[str, Any]
    signals: dict[str, Any]
    coverage: dict[str, Any]
    signal_strength: str
    confidence: str
    uncertainty_notes: list[str]
    alternative_explanations: list[str]
    evidence: list[tuple[str, str, dict[str, Any]]] = field(default_factory=list)


@dataclass
class ClusterDetectionResult:
    candidates: list[ClusterCandidate]
    stats: dict[str, Any]


def detect_clusters(
    g: nx.DiGraph, pairs: list[SimilarPair], posts: list[Post], scores: dict[str, float | None],
    observed_accounts: set[str], list_completeness: dict[tuple[str, str], str],
    node_community: dict[str, int], cfg: GraphConfig, deadline: Deadline,
    simhash_max_distance: int,
) -> ClusterDetectionResult:
    cc = cfg.cluster
    sim = [p for p in pairs if p.jaccard >= cc.jaccard_threshold and p.shared >= cc.min_shared_targets
           and g.out_degree(p.a) >= cc.min_out_degree and g.out_degree(p.b) >= cc.min_out_degree]
    stats: dict[str, Any] = {"similar_pairs": len(sim), "groups_found": 0, "skipped_too_small": 0,
                             "skipped_too_large": 0}
    if not sim:
        return ClusterDetectionResult([], stats)

    sim_graph: nx.Graph = nx.Graph()
    sim_weight: dict[tuple[str, str], float] = {}
    for p in sim:
        sim_graph.add_edge(p.a, p.b, weight=p.jaccard)
        sim_weight[(p.a, p.b)] = p.jaccard
    groups = nx.community.louvain_communities(sim_graph, weight="weight", seed=cfg.louvain_seed)
    groups = sorted((sorted(c) for c in groups), key=lambda c: (-len(c), c[0]))
    stats["groups_found"] = len(groups)

    posts_by_author: dict[str, list[Post]] = {}
    for p in posts:
        posts_by_author.setdefault(p.author, []).append(p)
    pop_threshold = in_degree_threshold(g, cc.popular_target_percentile)

    candidates: list[ClusterCandidate] = []
    for members in groups:
        deadline.check("cluster evidence")
        if len(members) < cc.min_cluster_size:
            stats["skipped_too_small"] += 1
            continue
        if len(members) > cc.max_cluster_size:
            stats["skipped_too_large"] += 1
            continue
        candidates.append(_assess(g, members, sim_weight, posts_by_author, scores, observed_accounts,
                                  list_completeness, node_community, pop_threshold, cfg,
                                  simhash_max_distance))
    return ClusterDetectionResult(candidates, stats)


def _assess(
    g: nx.DiGraph, members: list[str], sim_weight: dict[tuple[str, str], float],
    posts_by_author: dict[str, list[Post]], scores: dict[str, float | None],
    observed_accounts: set[str], list_completeness: dict[tuple[str, str], str],
    node_community: dict[str, int], pop_threshold: float, cfg: GraphConfig, simhash_max_distance: int,
) -> ClusterCandidate:
    cc = cfg.cluster
    n = len(members)
    mset = set(members)
    possible_pairs = n * (n - 1) / 2
    evidence: list[tuple[str, str, dict[str, Any]]] = []

    # ---- structure
    sub = g.subgraph(members)
    internal_edges = sub.number_of_edges()
    mutual_pairs = sum(1 for a, b in combinations(members, 2) if g.has_edge(a, b) and g.has_edge(b, a))
    total_out = sum(g.out_degree(m) for m in members)
    in_cluster_pairs = [(a, b) for a, b in combinations(members, 2) if (a, b) in sim_weight]
    mean_j = (sum(sim_weight[p] for p in in_cluster_pairs) / len(in_cluster_pairs)) if in_cluster_pairs else 0.0
    reciprocity = mutual_pairs / possible_pairs
    structure = {
        "member_count": n,
        "internal_follow_density": round(internal_edges / (n * (n - 1)), 4),
        "mutual_pair_fraction": round(reciprocity, 4),
        "internal_edge_share_of_member_follows": round(internal_edges / total_out, 4) if total_out else None,
        "similar_pair_fraction": round(len(in_cluster_pairs) / possible_pairs, 4),
        "mean_pair_jaccard": round(mean_j, 4),
        "follow_graph_communities_spanned": len({node_community[m] for m in members if m in node_community}),
    }

    # ---- shared follow targets (excluding the members themselves)
    counter: Counter[str] = Counter()
    for m in members:
        counter.update(t for t in g.successors(m) if t not in mset)
    need = max(2, math.ceil(cc.shared_target_member_share * n))
    shared = sorted(((t, c) for t, c in counter.items() if c >= need), key=lambda x: (-x[1], x[0]))
    # Popularity is measured *excluding the members' own follows*, otherwise the group would make its
    # own targets look popular.
    popular_share = (sum(1 for t, c in shared if g.in_degree(t) - c >= pop_threshold) / len(shared)
                     if shared else None)
    targets = {"shared_target_count": len(shared), "required_members_per_target": need,
               "popular_target_share": None if popular_share is None else round(popular_share, 4),
               "top_shared_targets": [{"account": t, "followed_by_members": c} for t, c in shared[:10]]}
    evidence.append((
        "structural_similarity",
        f"{n} accounts follow strongly overlapping sets of accounts (mean pairwise Jaccard {mean_j:.2f}; "
        f"{structure['similar_pair_fraction']:.0%} of member pairs above threshold).", structure))
    evidence.append((
        "shared_follow_targets",
        f"{len(shared)} accounts outside the group are each followed by at least {need} of its {n} members.",
        targets))

    # ---- repeated content across members
    content: dict[str, Any] = {"evaluated": False}
    content_present = False
    eligible = {m: posts_by_author.get(m, []) for m in members
                if len(posts_by_author.get(m, [])) >= cc.min_member_posts_for_content}
    all_posts = [p for ps in eligible.values() for p in ps if p.content_hash or p.simhash]
    if len(eligible) >= 2 and 0 < len(all_posts) <= _MAX_POSTS_FOR_CONTENT:
        labels = duplicate_components([(p.content_hash, p.simhash) for p in all_posts], simhash_max_distance)
        authors_by_label: dict[int, set[str]] = {}
        for p, lab in zip(all_posts, labels, strict=True):
            authors_by_label.setdefault(lab, set()).add(p.author)
        cross = sum(1 for lab in labels if len(authors_by_label[lab]) >= 2)
        ratio = cross / len(all_posts)
        groups = sum(1 for a in authors_by_label.values() if len(a) >= 2)
        content_present = ratio >= cc.content_duplication_threshold
        content = {"evaluated": True, "members_with_enough_posts": len(eligible),
                   "posts_considered": len(all_posts), "posts_duplicated_across_members": cross,
                   "cross_member_duplicate_ratio": round(ratio, 4), "duplicate_groups": groups,
                   "threshold": cc.content_duplication_threshold, "signal_present": content_present}
        evidence.append((
            "content_duplication",
            f"{cross} of {len(all_posts)} posts ({ratio:.0%}) by {len(eligible)} members repeat text "
            f"that another member also posted, in {groups} duplicate group(s).", content))

    # ---- temporal synchronisation
    sync = sync_lift({m: [p.ts for p in ps] for m, ps in eligible.items()}, cc.sync_window_seconds,
                     cc.sync_min_posts_per_member) if eligible else None
    temporal: dict[str, Any] = {"evaluated": False}
    temporal_present = False
    if sync is not None and sync.lift is not None:
        temporal_present = sync.lift >= cc.sync_lift_threshold and sync.observed >= cc.sync_min_observed_pairs
        temporal = {"evaluated": True, "window_seconds": cc.sync_window_seconds,
                    "observed_cross_member_coposts": sync.observed,
                    "expected_under_uniform_timing": round(sync.expected, 2), "lift": round(sync.lift, 2),
                    "members_used": sync.members_used, "threshold": cc.sync_lift_threshold,
                    "signal_present": temporal_present}
        evidence.append((
            "temporal_synchrony",
            f"Members posted within {cc.sync_window_seconds:g}s of each other {sync.observed} times, "
            f"{sync.lift:.1f}x what uniformly random timing would give.", temporal))
    elif sync is not None:
        temporal["reason"] = sync.note

    # ---- member risk
    scored = {m: scores[m] for m in members if scores.get(m) is not None}
    risk: dict[str, Any] = {"evaluated": False, "members_scored": len(scored)}
    risk_present = False
    if len(scored) >= math.ceil(n / 2):
        elevated = sum(1 for v in scored.values() if v is not None and v >= cc.elevated_member_score)
        share = elevated / len(scored)
        risk_present = share >= cc.elevated_member_share
        risk = {"evaluated": True, "members_scored": len(scored), "members_elevated": elevated,
                "elevated_share": round(share, 4),
                "mean_score": round(sum(v for v in scored.values() if v is not None) / len(scored), 2),
                "elevated_threshold": cc.elevated_member_score, "signal_present": risk_present}
        evidence.append((
            "member_risk",
            f"{elevated} of {len(scored)} scored members have account risk of at least "
            f"{cc.elevated_member_score:g} (mean {risk['mean_score']}).", risk))

    # ---- coverage, strength, confidence
    obs_frac = len(mset & observed_accounts) / n
    complete_following = sum(1 for m in members if list_completeness.get((m, "following")) == "complete") / n
    coverage = {"members_with_profile_observation": round(obs_frac, 4),
                "members_with_complete_following_list": round(complete_following, 4),
                "members_with_enough_posts": len(eligible)}
    behavioural = sum((content_present, temporal_present, risk_present))
    strength = "low" if behavioural == 0 else "moderate" if behavioural == 1 else "high"
    confident = obs_frac >= cc.min_observation_fraction and complete_following >= cc.min_complete_list_fraction
    confidence = "moderate" if confident else "low"
    evidence.append(("coverage", f"{obs_frac:.0%} of members have a profile observation and "
                     f"{complete_following:.0%} have a complete following list.", coverage))

    uncertainty: list[str] = []
    if not confident:
        uncertainty.append("Coverage is below the configured minimum, so overlap is measured on incomplete "
                           "data and confidence is capped at 'low'.")
    if not content.get("evaluated"):
        uncertainty.append("Repeated-content evidence could not be evaluated (too few members with enough posts).")
    if not temporal.get("evaluated"):
        uncertainty.append("Timing evidence could not be evaluated (too few members with enough posts).")
    if not risk.get("evaluated"):
        uncertainty.append("Too few members have an account risk score to use member risk as evidence.")
    uncertainty.append("Timing baseline assumes uniformly random posting; real daily rhythms raise the "
                       "expected overlap for organic accounts, so moderate lift is weak evidence.")

    alternatives = ["Shared interests: a fandom, hobby group or community can follow the same accounts."]
    if reciprocity >= cc.high_reciprocity_threshold:
        alternatives.append("Members follow each other mutually, which is typical of friends, teams or organisations.")
    if popular_share is not None and popular_share >= 0.5:
        alternatives.append("Most shared targets are popular accounts, so overlap is partly expected by chance.")
    if behavioural == 0:
        alternatives.append("No repeated-content, timing or risk evidence supports coordination; structural "
                            "similarity alone is common in organic communities.")
    if not confident:
        alternatives.append("Relationship lists are incomplete, so apparent overlap may differ in the full data.")

    member_metrics = {
        m: {"out_degree": g.out_degree(m),
            "follows_other_members": sum(1 for s in g.successors(m) if s in mset),
            "mean_jaccard_to_members": round(
                sum(w for (a, b), w in sim_weight.items() if m in (a, b) and a in mset and b in mset)
                / max(1, n - 1), 4),
            "risk_score": scores.get(m)}
        for m in members}

    metrics = {**structure, **{"targets": targets}}
    signals = {"structural": True, "content_duplication": content, "temporal_synchrony": temporal,
               "member_risk": risk}
    return ClusterCandidate(members, member_metrics, metrics, signals, coverage, strength, confidence,
                            uncertainty, alternatives, evidence)
