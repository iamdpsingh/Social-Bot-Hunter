import random
import unittest

from sbh.ingestion import fingerprint as fp


class Fingerprints(unittest.TestCase):
    def test_exact_hash_ignores_case_and_whitespace_but_not_words(self):
        self.assertEqual(fp.content_hash("Hello   World"), fp.content_hash("hello world"))
        self.assertNotEqual(fp.content_hash("hello world"), fp.content_hash("hello there"))

    def test_simhash_ignores_rotating_links_and_mentions(self):
        a = fp.simhash64("Huge giveaway today only claim your reward now http://bit.ly/aaa111 @one #win")
        b = fp.simhash64("Huge giveaway today only claim your reward now http://bit.ly/zzz999 @two #win")
        self.assertEqual(a, b)

    def test_unrelated_texts_are_far_apart(self):
        a = fp.simhash64("the quick brown fox jumps over the lazy dog near the river bank")
        b = fp.simhash64("completely different words about gardening recipes and morning coffee today")
        self.assertGreater(fp.hamming(a, b), 15)

    def test_short_texts_are_not_simhashed(self):
        self.assertIsNone(fp.simhash64("too short"))

    def test_components_group_exact_and_near_duplicates_only(self):
        t = "Limited offer on premium followers grab the deal before it ends http://x.co/{} @a"
        items = [(fp.content_hash(t.format("1")), fp.simhash64(t.format("1"))),
                 (fp.content_hash(t.format("2")), fp.simhash64(t.format("2"))),
                 ("same", None), ("same", None),
                 (fp.content_hash("a b c d e f g"), fp.simhash64("garden cricket morning recipe holiday museum bridge"))]
        lab = fp.duplicate_components(items, 6)
        self.assertEqual(lab[0], lab[1])
        self.assertEqual(lab[2], lab[3])
        self.assertEqual(len({lab[0], lab[2], lab[4]}), 3)

    def test_banded_search_matches_brute_force(self):
        rng = random.Random(7)
        base = [rng.getrandbits(64) for _ in range(40)]
        sims = []
        for b in base:
            sims.append(b)
            sims.append(b ^ sum(1 << rng.randrange(64) for _ in range(rng.randint(0, 6))))  # <= 6 bit flips
        items = [(None, s) for s in sims]
        lab = fp.duplicate_components(items, 6)
        # brute force union-find
        parent = list(range(len(sims)))

        def find(x):
            while parent[x] != x:
                x = parent[x]
            return x
        for i in range(len(sims)):
            for j in range(i + 1, len(sims)):
                if fp.hamming(sims[i], sims[j]) <= 6:
                    parent[max(find(i), find(j))] = min(find(i), find(j))
        brute = [find(i) for i in range(len(sims))]
        same = lambda lab_, i, j: lab_[i] == lab_[j]  # noqa: E731
        for i in range(len(sims)):
            for j in range(len(sims)):
                self.assertEqual(same(lab, i, j), same(brute, i, j), (i, j))


if __name__ == "__main__":
    unittest.main()
