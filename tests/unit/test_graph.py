import random
import unittest
from dataclasses import replace
from itertools import combinations

import networkx as nx

from sbh.config import load_config
from sbh.graph.build import Deadline, build_graph, graphs_by_platform
from sbh.graph.clusters import detect_clusters
from sbh.graph.community import detect_communities, node_community_index
from sbh.graph.compare import diff_edge_sets
from sbh.graph.metrics import graph_summary, node_metrics
from sbh.graph.similarity import jaccard, neighbour_pairs
from sbh.graph.temporal import sync_lift
from sbh.shared.errors import GraphLimitExceeded
from sbh.shared.models import Post

CFG = load_config()
LIM = CFG.graph.limits


def dl():
    return Deadline(60)


def graph(edges, platform="x"):
    return build_graph(platform, edges, LIM)


class Directionality(unittest.TestCase):
    def test_follow_is_directed_and_reverse_is_not_inferred(self):
        g = graph([("a", "b")])
        self.assertTrue(g.has_edge("a", "b"))
        self.assertFalse(g.has_edge("b", "a"))
        self.assertEqual((g.out_degree("a"), g.in_degree("a")), (1, 0))
        self.assertEqual((g.out_degree("b"), g.in_degree("b")), (0, 1))

    def test_mutual_follow_needs_both_edges(self):
        g = graph([("a", "b"), ("b", "a"), ("a", "c")])
        m = node_metrics(g, [], 1, complete_following={"a", "b", "c"})
        self.assertEqual((m["a"].checkable_follows, m["a"].mutual_count), (2, 1))  # b follows back, c does not

    def test_follow_back_is_only_judged_where_the_other_list_is_complete(self):
        g = graph([("a", "b"), ("a", "c")])
        m = node_metrics(g, [], 1, complete_following={"b"})  # c's following list was not collected
        self.assertEqual((m["a"].checkable_follows, m["a"].mutual_count), (1, 0))

    def test_identity_namespaces_never_merge_across_platforms(self):
        gs = graphs_by_platform([("x", "alice", "bob"), ("tiktok", "alice", "carol")], LIM)
        self.assertEqual(set(gs), {"x", "tiktok"})
        self.assertEqual(set(gs["x"].nodes), {"alice", "bob"})
        self.assertEqual(set(gs["tiktok"].nodes), {"alice", "carol"})
        self.assertFalse(set(gs["x"].edges) & set(gs["tiktok"].edges))


class Similarity(unittest.TestCase):
    def test_jaccard_basics(self):
        self.assertEqual(jaccard({"a", "b"}, {"b", "c"}), 1 / 3)
        self.assertEqual(jaccard(set(), set()), 0.0)

    def test_pair_members_are_excluded_from_each_others_sets(self):
        # a and b follow each other and the same targets t1..t3; the mutual follow must not inflate overlap
        edges = [("a", "b"), ("b", "a")] + [(x, f"t{i}") for x in "ab" for i in range(3)]
        pairs, _ = neighbour_pairs(graph(edges), direction="out", min_degree=1, min_shared=1,
                                   max_posting=50, limits=LIM, deadline=dl())
        (p,) = pairs
        self.assertEqual((p.a, p.b, p.shared, p.jaccard), ("a", "b", 3, 1.0))

    def test_matches_brute_force_on_random_graph(self):
        rng = random.Random(11)
        nodes = [f"n{i}" for i in range(40)]
        edges = [(a, b) for a in nodes for b in rng.sample(nodes, 8) if a != b]
        g = graph(edges)
        pairs, _ = neighbour_pairs(g, direction="out", min_degree=3, min_shared=2, max_posting=1000,
                                   limits=LIM, deadline=dl())
        got = {(p.a, p.b): (p.jaccard, p.shared) for p in pairs}
        want = {}
        for a, b in combinations(sorted(g.nodes), 2):
            if g.out_degree(a) < 3 or g.out_degree(b) < 3:
                continue
            sa, sb = set(g.successors(a)) - {b}, set(g.successors(b)) - {a}
            if len(sa & sb) >= 2:
                want[(a, b)] = (jaccard(sa, sb), len(sa & sb))
        self.assertEqual(got.keys(), want.keys())
        for k in want:
            self.assertAlmostEqual(got[k][0], want[k][0])
            self.assertEqual(got[k][1], want[k][1])

    def test_in_direction_compares_followers_not_followees(self):
        edges = [(f"f{i}", t) for i in range(5) for t in ("x", "y")]
        pairs, _ = neighbour_pairs(graph(edges), direction="in", min_degree=3, min_shared=3, max_posting=50,
                                   limits=LIM, deadline=dl())
        self.assertEqual([(p.a, p.b, p.jaccard) for p in pairs], [("x", "y", 1.0)])

    def test_hub_targets_skip_candidate_generation_and_are_reported(self):
        edges = [(f"u{i}", "celebrity") for i in range(6)]
        pairs, stats = neighbour_pairs(graph(edges), direction="out", min_degree=1, min_shared=1, max_posting=3,
                                       limits=LIM, deadline=dl())
        self.assertEqual(pairs, [])
        self.assertEqual(stats["skipped_hub_targets"], 1)

    def test_limits_raise_instead_of_truncating(self):
        edges = [(f"u{i}", "t") for i in range(10)]
        with self.assertRaises(GraphLimitExceeded):
            build_graph("x", edges, replace(LIM, max_edges=5))
        with self.assertRaises(GraphLimitExceeded):
            build_graph("x", edges, replace(LIM, max_nodes=5))
        with self.assertRaises(GraphLimitExceeded):
            neighbour_pairs(graph([(f"u{i}", f"t{j}") for i in range(8) for j in range(3)]), direction="out",
                            min_degree=1, min_shared=1, max_posting=50, limits=replace(LIM, max_pairs=5),
                            deadline=dl())

    def test_runtime_deadline_raises(self):
        ticks = iter([0.0] + [100.0] * 1000)
        d = Deadline(1.0, clock=lambda: next(ticks))
        with self.assertRaises(GraphLimitExceeded):
            neighbour_pairs(graph([(f"u{i}", "t") for i in range(5)]), direction="out", min_degree=1,
                            min_shared=1, max_posting=50, limits=LIM, deadline=d)


class StructureAndTime(unittest.TestCase):
    def test_summary_and_communities_are_deterministic(self):
        g = nx.DiGraph()
        for grp in (["a", "b", "c", "d"], ["w", "x", "y", "z"]):
            g.add_edges_from((u, v) for u in grp for v in grp if u != v)
        g.add_edge("a", "w")
        s = graph_summary(g)
        self.assertEqual((s["nodes"], s["edges"]), (8, 25))
        self.assertGreater(s["reciprocity"], 0.9)
        c1, c2 = detect_communities(g, 42), detect_communities(g, 42)
        self.assertEqual(c1, c2)
        self.assertEqual(sorted(map(sorted, c1)), [["a", "b", "c", "d"], ["w", "x", "y", "z"]])
        self.assertEqual(node_community_index(c1)["a"], node_community_index(c1)["d"])

    def test_synchronised_posters_show_high_lift_random_posters_do_not(self):
        rng = random.Random(5)
        day = 86400.0
        bursts = [i * 6 * 3600.0 for i in range(40)]
        sync = {f"m{k}": [b + rng.uniform(0, 20) for b in bursts] for k in range(5)}
        r = sync_lift(sync, window=60, min_posts=3)
        self.assertGreater(r.lift, 20)
        organic = {f"m{k}": [rng.uniform(0, 10 * day) for _ in range(40)] for k in range(5)}
        self.assertLess(sync_lift(organic, window=60, min_posts=3).lift, 3.0)

    def test_sync_lift_declines_when_evidence_is_thin(self):
        r = sync_lift({"a": [1.0, 2.0, 3.0], "b": [1.0]}, window=60, min_posts=3)
        self.assertIsNone(r.lift)
        self.assertIsNotNone(r.note)
        self.assertIsNone(sync_lift({"a": [5.0] * 3, "b": [5.0] * 3}, 60, 3).lift)  # zero time span


class ScanComparison(unittest.TestCase):
    def test_removal_is_confirmed_only_by_a_complete_list(self):
        earlier = {("a", "b"), ("a", "c"), ("d", "e")}
        later = {("a", "b")}
        later_cov = {("a", "following"): "complete", ("e", "followers"): "partial"}
        d = diff_edge_sets(earlier, later, {}, later_cov)
        self.assertEqual(d.confirmed_removed, {("a", "c")})      # a's following list is complete now
        self.assertEqual(d.not_reobserved, {("d", "e")})         # nothing complete covers d->e
        self.assertEqual(d.unchanged, {("a", "b")})

    def test_addition_is_confirmed_only_if_earlier_collection_was_complete(self):
        later = {("a", "b"), ("c", "d")}
        earlier_cov = {("a", "following"): "complete", ("c", "following"): "partial"}
        d = diff_edge_sets(set(), later, earlier_cov, {})
        self.assertEqual(d.confirmed_added, {("a", "b")})
        self.assertEqual(d.newly_observed, {("c", "d")})

    def test_target_side_complete_followers_list_also_proves_absence(self):
        d = diff_edge_sets({("a", "b")}, set(), {}, {("b", "followers"): "complete"})
        self.assertEqual(d.confirmed_removed, {("a", "b")})

    def test_unknown_coverage_never_yields_confirmed_changes(self):
        d = diff_edge_sets({("a", "b")}, {("c", "d")}, {("a", "following"): "unknown"}, {("a", "following"): "unknown"})
        self.assertFalse(d.confirmed_added or d.confirmed_removed)
        self.assertEqual(d.summary()["newly_observed"] + d.summary()["not_reobserved"], 2)


# ----------------------------------------------------------------------------- cluster logic
GC = CFG.graph


def ring_graph(members, shared, extra=2):
    edges = []
    for i, m in enumerate(members):
        edges += [(m, t) for t in shared]
        edges += [(m, f"own_{m}_{k}") for k in range(extra)]
    return graph(edges)


class ClusterLogic(unittest.TestCase):
    members = [f"m{i}" for i in range(6)]
    shared = [f"t{i}" for i in range(20)]

    def run_detect(self, g, posts=(), scores=None, observed=None, cov=None):
        pairs, _ = neighbour_pairs(g, direction="out", min_degree=10, min_shared=2, max_posting=300,
                                   limits=LIM, deadline=dl())
        scores = scores if scores is not None else {}
        observed = set(self.members) if observed is None else observed
        cov = cov if cov is not None else {(m, "following"): "complete" for m in self.members}
        return detect_clusters(g, pairs, list(posts), scores, observed, cov, {}, GC, dl(),
                               CFG.features.simhash_max_distance)

    def test_overlapping_followers_are_surfaced_but_structure_alone_is_low_strength(self):
        res = self.run_detect(ring_graph(self.members, self.shared))
        (c,) = res.candidates
        self.assertEqual(sorted(c.members), self.members)
        self.assertEqual(c.signal_strength, "low")
        self.assertTrue(any("structural similarity alone" in a for a in c.alternative_explanations))
        self.assertTrue(c.uncertainty_notes)

    def test_independent_behavioural_evidence_raises_strength(self):
        tmpl = "Huge giveaway claim your reward now before it ends today only"
        from sbh.ingestion.fingerprint import content_hash, simhash64
        posts = [Post(m, 1000.0 * k + j, content_hash(tmpl), simhash64(tmpl))
                 for j, m in enumerate(self.members) for k in range(6)]
        scores = {m: 80.0 for m in self.members}
        res = self.run_detect(ring_graph(self.members, self.shared), posts, scores)
        (c,) = res.candidates
        self.assertTrue(c.signals["content_duplication"]["signal_present"])
        self.assertTrue(c.signals["member_risk"]["signal_present"])
        self.assertEqual(c.signal_strength, "high")

    def test_mutual_follow_group_gets_a_friends_alternative_explanation(self):
        g = graph([(a, b) for a in self.members for b in self.members if a != b]
                  + [(m, f"t{i}") for m in self.members for i in range(8)])
        (c,) = self.run_detect(g).candidates
        self.assertTrue(any("follow each other mutually" in a for a in c.alternative_explanations))
        self.assertEqual(c.signal_strength, "low")

    def test_confidence_is_capped_by_coverage(self):
        g = ring_graph(self.members, self.shared)
        (full,) = self.run_detect(g).candidates
        self.assertEqual(full.confidence, "moderate")
        (thin,) = self.run_detect(g, observed=set(), cov={}).candidates
        self.assertEqual(thin.confidence, "low")
        self.assertTrue(any("incomplete" in a for a in thin.alternative_explanations))

    def test_unrelated_accounts_form_no_cluster(self):
        rng = random.Random(3)
        pool = [f"t{i}" for i in range(500)]
        g = graph([(m, t) for m in self.members for t in rng.sample(pool, 20)])
        self.assertEqual(self.run_detect(g).candidates, [])

    def test_too_small_and_too_large_groups_are_skipped_and_counted(self):
        g = ring_graph(self.members[:2], self.shared)
        res = self.run_detect(g)
        self.assertEqual(res.candidates, [])
        self.assertEqual(res.stats["skipped_too_small"], 1)

    def test_clusters_are_deterministic(self):
        g = ring_graph(self.members, self.shared)
        a, b = self.run_detect(g), self.run_detect(g)
        self.assertEqual([c.members for c in a.candidates], [c.members for c in b.candidates])


if __name__ == "__main__":
    unittest.main()
