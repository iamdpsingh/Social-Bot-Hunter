"""Scale smoke tests: how the graph stage and the import path behave on larger inputs.

These measure and bound runtime/memory on *synthetic random graphs*; they are not a claim about
real-world performance. Observed timings are recorded in docs/testing-and-validation.md.
"""

import random
import resource
import time
import unittest

from sbh.config import load_config
from sbh.graph.build import Deadline, build_graph
from sbh.graph.clusters import detect_clusters
from sbh.graph.community import detect_communities, node_community_index
from sbh.graph.metrics import node_metrics
from sbh.graph.similarity import neighbour_pairs
from sbh.pipeline.run import import_dataset
from tests.support import DbTestCase, acct, edge, manifest, write_dir

CFG = load_config()


def rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


class GraphScale(unittest.TestCase):
    def test_60k_edges_with_a_planted_ring_complete_quickly_and_find_the_ring(self):
        rng = random.Random(1)
        accounts = [f"u{i}" for i in range(2000)]
        universe = [f"t{i}" for i in range(6000)]
        edges = [(a, t) for a in accounts for t in rng.sample(universe, 30)]
        ring = [f"ring{i}" for i in range(12)]
        shared = rng.sample(universe, 28)
        edges += [(m, t) for m in ring for t in shared + rng.sample(universe, 2)]
        t0, mem0 = time.perf_counter(), rss_mb()
        g = build_graph("x", edges, CFG.graph.limits)
        pairs, stats = neighbour_pairs(g, direction="out", min_degree=10, min_shared=2, max_posting=300,
                                       limits=CFG.graph.limits, deadline=Deadline(120))
        nm = node_metrics(g, pairs, 10, set())
        comms = detect_communities(g, 42)
        res = detect_clusters(g, pairs, [], {}, set(ring), {}, node_community_index(comms), CFG.graph,
                              Deadline(120), 6)
        elapsed, mem = time.perf_counter() - t0, rss_mb() - mem0
        print(f"\n[scale] edges={g.number_of_edges()} nodes={g.number_of_nodes()} pairs={len(pairs)} "
              f"communities={len(comms)} elapsed={elapsed:.1f}s rss_delta={mem:.0f}MB")
        self.assertLess(elapsed, 90)
        self.assertEqual(len(nm), g.number_of_nodes())
        found = [c for c in res.candidates if set(ring) <= set(c.members)]
        self.assertEqual(len(found), 1)
        self.assertEqual(len(found[0].members), 12)   # random accounts did not leak into the cluster


class ImportScale(DbTestCase):
    def test_import_of_25k_edges_persists_and_analyses_within_bounds(self):
        rng = random.Random(2)
        ids = [f"u{i:04d}" for i in range(1000)]
        rels = [edge(a, b) for a in ids for b in rng.sample([x for x in ids if x != a], 25)]
        d = write_dir(self.tmp / "big", man=manifest(), accounts=[acct(i) for i in ids], relationships=rels)
        t0 = time.perf_counter()
        res = import_dataset(self.db, d, CFG)
        elapsed = time.perf_counter() - t0
        print(f"\n[scale] import edges={len(rels)} accounts={len(ids)} elapsed={elapsed:.1f}s status={res.status}")
        self.assertEqual(res.status, "complete")
        self.assertEqual(self.count("relationship_edges"), len(rels))
        self.assertLess(elapsed, 120)


if __name__ == "__main__":
    unittest.main()
