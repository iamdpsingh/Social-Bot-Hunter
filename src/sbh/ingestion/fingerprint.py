"""Content fingerprints: exact hash plus a 64-bit SimHash for near-duplicate detection.

Only the fingerprints are stored; raw post text never reaches the database. SimHash is
computed over 3-word shingles, so posts that share a template but differ in a link or a
number land a few bits apart, while unrelated posts land ~32 bits apart.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata

_TOKEN = re.compile(r"\w+", re.UNICODE)
_URL = re.compile(r"(?:https?://|www\.)\S+", re.IGNORECASE)
_MENTION = re.compile(r"@\w+")
MIN_TOKENS_FOR_SIMHASH = 5


def normalise_text(text: str) -> str:
    return unicodedata.normalize("NFKC", text).casefold().strip()


def tokens(text: str) -> list[str]:
    return _TOKEN.findall(normalise_text(text))


def content_hash(text: str) -> str:
    """Exact-match fingerprint of the whitespace/case-normalised text."""
    canonical = " ".join(tokens(text))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _h64(value: str) -> int:
    return int.from_bytes(hashlib.blake2b(value.encode("utf-8"), digest_size=8).digest(), "big")


def simhash64(text: str) -> int | None:
    """Return a 64-bit SimHash, or None when the text is too short to fingerprint reliably.

    URLs and @mentions are replaced by fixed placeholders first: spam templates routinely rotate
    the link or the mentioned handle, and that should not hide the repetition. The exact
    ``content_hash`` is unaffected and still distinguishes such posts.
    """
    toks = tokens(_MENTION.sub(" mentionplaceholder ", _URL.sub(" urlplaceholder ", text)))
    if len(toks) < MIN_TOKENS_FOR_SIMHASH:
        return None
    shingles = [" ".join(toks[i : i + 3]) for i in range(len(toks) - 2)]
    votes = [0] * 64
    for sh in shingles:
        h = _h64(sh)
        for bit in range(64):
            votes[bit] += 1 if (h >> bit) & 1 else -1
    out = 0
    for bit in range(64):
        if votes[bit] > 0:
            out |= 1 << bit
    return out


def hamming(a: int, b: int) -> int:
    return (a ^ b).bit_count()


def duplicate_components(items: list[tuple[str | None, int | None]], max_distance: int) -> list[int]:
    """Group fingerprinted posts into exact/near-duplicate components.

    ``items[i]`` is ``(content_hash, simhash)``. Returns a component label per item. Posts are
    joined when their content hashes are equal, or when their SimHashes are within
    ``max_distance`` bits. Near matches are found by banding the 64 bits into
    ``max_distance + 1`` chunks: two values within that distance must agree on at least one
    chunk (pigeonhole), so only same-chunk candidates need an exact Hamming check.
    """
    n = len(items)
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    by_hash: dict[str, int] = {}
    for i, (h, _) in enumerate(items):
        if h is not None:
            if h in by_hash:
                union(i, by_hash[h])
            else:
                by_hash[h] = i

    bands = max_distance + 1
    edges = [round(64 * k / bands) for k in range(bands + 1)]
    for k in range(bands):
        lo, hi = edges[k], edges[k + 1]
        mask = ((1 << (hi - lo)) - 1) << lo
        buckets: dict[int, list[int]] = {}
        for i, (_, s) in enumerate(items):
            if s is not None:
                buckets.setdefault(s & mask, []).append(i)
        for members in buckets.values():
            if len(members) < 2:
                continue
            # Compare each member with the bucket's first still-distinct representatives.
            reps: list[int] = []
            for i in members:
                si = items[i][1]
                assert si is not None
                for r in reps:
                    sr = items[r][1]
                    assert sr is not None
                    if hamming(si, sr) <= max_distance:
                        union(i, r)
                        break
                else:
                    reps.append(i)
    return [find(i) for i in range(n)]
