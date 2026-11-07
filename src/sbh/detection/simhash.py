"""64-bit SimHash text fingerprinting and near-duplicate clustering.

Uses 64-bit integer bitvectors with 3-gram character tokenization and
word n-grams to detect coordinated duplicate or templated bot postings.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any


def _tokenize_text(text: str) -> list[str]:
    """Normalize and tokenize text into words and 3-char sub-shingles."""
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    words = [w for w in cleaned.split() if len(w) > 1]
    tokens = list(words)
    # Character 3-grams
    compact = re.sub(r"\s+", "", cleaned)
    if len(compact) >= 3:
        for i in range(len(compact) - 2):
            tokens.append(compact[i : i + 3])
    return tokens or [text.lower()]


def _fnv64(s: str) -> int:
    """Compute 64-bit FNV-1a hash of a token."""
    h = hashlib.md5(s.encode("utf-8"), usedforsecurity=False).digest()
    return int.from_bytes(h[:8], byteorder="big", signed=False)


def compute_simhash(text: str) -> int:
    """Compute a 64-bit SimHash fingerprint for an arbitrary text string."""
    tokens = _tokenize_text(text)
    if not tokens:
        return 0

    v = [0] * 64
    for token in tokens:
        h = _fnv64(token)
        for i in range(64):
            bit = (h >> i) & 1
            v[i] += 1 if bit else -1

    fingerprint = 0
    for i in range(64):
        if v[i] > 0:
            fingerprint |= 1 << i
    return fingerprint


def hamming_distance(h1: int, h2: int) -> int:
    """Compute Hamming distance (number of differing bits) between two 64-bit hashes."""
    x = (h1 ^ h2) & 0xFFFFFFFFFFFFFFFF
    return bin(x).count("1")


def similarity_ratio(h1: int, h2: int) -> float:
    """Compute normalized similarity ratio in [0.0, 1.0] from Hamming distance."""
    d = hamming_distance(h1, h2)
    return max(0.0, min(1.0, 1.0 - (d / 64.0)))


@dataclass(frozen=True)
class SimHashCluster:
    """A cluster of near-duplicate messages sharing a common SimHash centroid."""

    cluster_id: str
    representative_text: str
    member_count: int
    account_ids: list[str]
    sample_texts: list[str]
    avg_pairwise_similarity: float
    max_hamming_distance: int


def cluster_texts(
    items: Sequence[dict[str, Any]],
    max_hamming_distance: int = 3,
) -> list[SimHashCluster]:
    """Group items with 'text' and 'account_id' into clusters within max_hamming_distance."""
    if not items:
        return []

    fingerprints = [
        (item.get("account_id", f"acc_{idx}"), item.get("text", ""), compute_simhash(item.get("text", "")))
        for idx, item in enumerate(items)
        if item.get("text")
    ]

    clusters: list[list[tuple[str, str, int]]] = []
    for acc_id, text, fp in fingerprints:
        placed = False
        for c in clusters:
            centroid_fp = c[0][2]
            if hamming_distance(centroid_fp, fp) <= max_hamming_distance:
                c.append((acc_id, text, fp))
                placed = True
                break
        if not placed:
            clusters.append([(acc_id, text, fp)])

    result: list[SimHashCluster] = []
    for idx, c in enumerate(clusters):
        if len(c) < 2:
            continue
        acc_ids = list({m[0] for m in c})
        texts = [m[1] for m in c]
        rep_text = texts[0]
        # Calculate avg similarity
        fps = [m[2] for m in c]
        max_dist = max(hamming_distance(fps[0], fp) for fp in fps)
        sims = [similarity_ratio(fps[0], fp) for fp in fps]
        avg_sim = round(float(sum(sims) / len(sims)), 4) if sims else 1.0

        result.append(
            SimHashCluster(
                cluster_id=f"simhash_cluster_{idx + 1:03d}",
                representative_text=rep_text,
                member_count=len(c),
                account_ids=acc_ids,
                sample_texts=texts[:5],
                avg_pairwise_similarity=avg_sim,
                max_hamming_distance=max_dist,
            )
        )

    result.sort(key=lambda x: x.member_count, reverse=True)
    return result
