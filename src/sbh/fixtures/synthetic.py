"""Deterministic SYNTHETIC dataset for tests and demos.

Everything here is invented. The manifest says ``collection_method: synthetic`` so scans made from
it are labelled as synthetic data everywhere. The planted groups ("truth") exist so tests can check
that the pipeline *finds what was planted*; that is a regression check, not a model evaluation, and
it says nothing about accuracy on real accounts.

Planted structure (platform ``x``):
  * 8 hubs       - popular accounts that many people follow (celebrity-style hubs)
  * 4 promoted   - ordinary-looking accounts a bot ring is boosting
  * 60 organic   - varied profiles, random posting times, mixed follows with some follow-backs
  * 8 friends    - mutually follow each other and one shared set of popular accounts: structurally
                   similar, but nothing else suggests coordination (the classic false-positive risk)
  * 8 obvious bots + 2 stealth bots - follow almost the same 24 accounts, rotate a few post
                   templates with changing links, and post in 12-hourly synchronised bursts
  * 5 sparse     - almost no data: should end up with "insufficient evidence"
  * 400 background accounts that appear only as follow targets (stubs, no profile data)
"""

from __future__ import annotations

import csv
import json
import random
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

COLLECTED_AT = datetime(2026, 9, 30, 12, 0, 0, tzinfo=UTC)

_FIRST = ["maya", "arjun", "liam", "noor", "zoe", "ravi", "emma", "kofi", "sana", "diego", "ines",
          "yuki", "omar", "lena", "tariq", "nina", "felix", "amara", "hugo", "priya", "marta", "jonas",
          "leila", "ben", "isha", "carlos", "mei", "oscar", "farah", "theo", "anya", "samir", "ella",
          "vikram", "chloe", "idris", "tara", "nico", "alma", "rohan"]
_LAST = ["k", "rao", "ng", "diaz", "stone", "okafor", "lee", "mehta", "silva", "berg", "khan", "ward"]
_WORDS = ("coffee morning match train weekend recipe garden camera lecture project deadline holiday "
          "market concert library bridge river mountain season festival painting guitar football "
          "cricket rainfall journey village station breakfast evening workshop podcast notebook "
          "harvest lantern museum bicycle thunder pottery orchard sunrise ferry cabinet blanket "
          "compass violin glacier meadow harbor kitchen puzzle postcard student teacher doctor "
          "builder baker sailor writer painter runner walker singer dancer driver farmer weaver "
          "quiet loud bright gentle sudden steady curious tired happy nervous proud lucky").split()
_TEMPLATES = [
    "Huge giveaway today only claim your reward now {link} {mention} #win",
    "Limited offer on premium followers grab the deal before it ends {link} {mention}",
    "You will not believe this crypto opportunity join the community today {link} {mention}",
    "Exclusive discount code unlocked for our early supporters check it out {link} {mention}",
    "Make money online from home with this simple trick learn how {link} {mention} #cash",
    "Win a free phone just follow and retweet to enter the draw {link} {mention} #free",
]


@dataclass
class SyntheticDataset:
    manifest: dict[str, Any]
    accounts: list[dict[str, Any]] = field(default_factory=list)
    relationships: list[dict[str, Any]] = field(default_factory=list)
    content: list[dict[str, Any]] = field(default_factory=list)
    truth: dict[str, list[str]] = field(default_factory=dict)


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def generate(seed: int = 42) -> SyntheticDataset:
    rng = random.Random(seed)
    ds = SyntheticDataset(manifest={})
    used_names: set[str] = set()
    bg = [f"b{i:04d}" for i in range(1, 401)]
    hubs = [f"h{i:03d}" for i in range(1, 9)]
    promoted = [f"p{i:03d}" for i in range(1, 5)]
    organic = [f"u{i:04d}" for i in range(1, 61)]
    friends = [f"g{i:02d}" for i in range(1, 9)]
    ring = [f"r{i:03d}" for i in range(1, 9)]
    stealth = ["r009", "r010"]
    sparse = [f"s{i:03d}" for i in range(1, 6)]
    follows: dict[str, set[str]] = {}

    def human_username() -> str:
        while True:
            name = rng.choice(_FIRST)
            style = rng.random()
            if style < 0.35:
                u = f"{name}_{rng.choice(_LAST)}"
            elif style < 0.6:
                u = f"{name}.{rng.choice(_LAST)}"
            elif style < 0.85:
                u = f"{name}{rng.randint(1, 99)}"
            else:
                u = f"{rng.choice(_WORDS)}_{name}"
            if u not in used_names:
                used_names.add(u)
                return u

    def account_row(pid: str, observed: datetime, *, username: str | None, followers: int | None,
                    following: int | None, posts: int | None, bio: bool | None, image: bool | None,
                    created_days: float | None, display: str | None = "") -> dict[str, Any]:
        return {
            "platform": "x", "platform_account_id": pid, "observed_at": _iso(observed),
            "username": username or "", "display_name": (display if display else (username or "").replace("_", " ").title()),
            "follower_count": "" if followers is None else followers,
            "following_count": "" if following is None else following,
            "post_count": "" if posts is None else posts,
            "has_bio": "" if bio is None else str(bio).lower(),
            "bio_length": "",
            "has_profile_image": "" if image is None else str(image).lower(),
            "has_display_name": "true" if username else "",
            "account_created_at": "" if created_days is None else _iso(COLLECTED_AT - timedelta(days=created_days)),
            "is_verified": "", "is_private": "",
        }

    def observed_recently() -> datetime:
        return COLLECTED_AT - timedelta(minutes=rng.randint(5, 360))

    # ---- hubs and promoted accounts
    for pid in hubs:
        ds.accounts.append(account_row(pid, observed_recently(), username=f"{rng.choice(_WORDS)}hq{pid[1:]}",
                                       followers=rng.randint(50_000, 2_000_000), following=rng.randint(40, 500),
                                       posts=rng.randint(6000, 30000), bio=True, image=True,
                                       created_days=rng.randint(2500, 4000)))
    for pid in promoted:
        ds.accounts.append(account_row(pid, observed_recently(), username=human_username(),
                                       followers=rng.randint(150, 600), following=rng.randint(100, 500),
                                       posts=rng.randint(300, 1500), bio=True, image=True,
                                       created_days=rng.randint(400, 1500)))

    # ---- organic accounts
    for pid in organic:
        age = rng.randint(200, 3000)
        followers = int(rng.lognormvariate(5.7, 0.8))
        ratio = rng.choice([0.3, 0.6, 1.0, 1.5, 2.5, 4.0, 7.0])
        following = max(20, int(followers * ratio))
        ds.accounts.append(account_row(
            pid, observed_recently(), username=human_username(), followers=followers, following=following,
            posts=int(age * rng.uniform(0.1, 3.0)), bio=rng.random() < 0.85, image=rng.random() < 0.92,
            created_days=age))
        f = set(rng.sample(hubs, rng.randint(2, 5)))
        f |= set(rng.sample(bg, rng.randint(10, 25)))
        f |= set(rng.sample([o for o in organic if o != pid], rng.randint(5, 12)))
        follows[pid] = f
    for pid in organic:  # organic accounts follow each other back about half the time
        for other in sorted(follows[pid] & set(organic)):
            if rng.random() < 0.5:
                follows[other].add(pid)

    # ---- friend group: mutual follows + the same four popular accounts
    fandom = rng.sample(hubs, 4)
    for pid in friends:
        age = rng.randint(300, 2500)
        followers = rng.randint(150, 900)
        ds.accounts.append(account_row(
            pid, observed_recently(), username=human_username(), followers=followers,
            following=int(followers * rng.uniform(0.6, 1.6)), posts=int(age * rng.uniform(0.3, 2.0)),
            bio=True, image=True, created_days=age))
        follows[pid] = {g for g in friends if g != pid} | set(fandom) | set(rng.sample(bg, 2))

    # ---- bot ring
    shared_targets = promoted + rng.sample(bg, 20)
    for pid in ring + stealth:
        omit = rng.choice(shared_targets)
        follows[pid] = {t for t in shared_targets if t != omit} | set(rng.sample(bg, 2))
    for k, pid in enumerate(ring):
        age = rng.randint(20, 45)
        earlier = COLLECTED_AT - timedelta(days=14, minutes=rng.randint(0, 600))
        grown = k % 2 == 0
        followers_now = rng.randint(150, 300) if grown else rng.randint(5, 40)
        following_now = rng.randint(1500, 2100)
        username = f"user{rng.randint(10**7, 10**8 - 1)}"
        ds.accounts.append(account_row(pid, observed_recently(), username=username, followers=followers_now,
                                       following=following_now, posts=int(age * rng.uniform(100, 150)),
                                       bio=False, image=False, created_days=age, display=username))
        ds.accounts.append(account_row(pid, earlier, username=username,
                                       followers=rng.randint(10, 25) if grown else max(1, followers_now - 3),
                                       following=following_now - rng.randint(50, 200), posts=int(age * 60),
                                       bio=False, image=False, created_days=age, display=username))
    for pid in stealth:
        age = rng.randint(400, 700)
        followers = rng.randint(400, 800)
        ds.accounts.append(account_row(pid, observed_recently(), username=human_username(),
                                       followers=followers, following=int(followers * rng.uniform(1.0, 1.6)),
                                       posts=int(age * rng.uniform(2, 4)), bio=True, image=True,
                                       created_days=age))

    # ---- sparse accounts: almost nothing known
    for k, pid in enumerate(sparse):
        ds.accounts.append(account_row(
            pid, observed_recently(), username=human_username() if k % 2 == 0 else None,
            followers=None if k < 2 else rng.randint(10, 50), following=rng.randint(10, 30) if k == 0 else None,
            posts=None, bio=None, image=None, created_days=None))
        follows[pid] = set(rng.sample(bg, rng.randint(2, 6)))

    # ---- relationship rows
    obs_time = COLLECTED_AT - timedelta(hours=2)
    for src in sorted(follows):
        for dst in sorted(follows[src]):
            ds.relationships.append({
                "platform": "x", "source_account_id": src, "target_account_id": dst,
                "relationship_type": "follows", "observed_at": _iso(obs_time), "verification_status": "source_asserted"})

    # ---- content
    cid = 0

    def add_post(author: str, ts: datetime, text: str) -> None:
        nonlocal cid
        cid += 1
        ds.content.append({"platform": "x", "platform_content_id": f"c{cid:06d}", "author_account_id": author,
                           "published_at": _iso(ts), "text": text, "like_count": rng.randint(0, 40),
                           "reply_count": rng.randint(0, 6), "share_count": rng.randint(0, 8)})

    def organic_post(author: str, lo: int, hi: int) -> None:
        for _ in range(rng.randint(lo, hi)):
            ts = COLLECTED_AT - timedelta(seconds=rng.randint(3600, 30 * 86400))
            add_post(author, ts, " ".join(rng.sample(_WORDS, rng.randint(9, 16))))

    for pid in organic:
        organic_post(pid, 8, 16)
    for pid in friends:
        organic_post(pid, 8, 14)
    burst = COLLECTED_AT - timedelta(days=30)
    bursts = []
    while burst < COLLECTED_AT - timedelta(hours=1):
        bursts.append(burst + timedelta(seconds=rng.randint(0, 90)))
        burst += timedelta(hours=12)
    for b_idx, bt in enumerate(bursts):
        template = _TEMPLATES[b_idx % len(_TEMPLATES)]
        for pid in ring + stealth:
            link = "http://bit.ly/" + "".join(rng.choice("abcdefghjkmnpqrstuvwxyz23456789") for _ in range(6))
            add_post(pid, bt + timedelta(seconds=rng.uniform(0, 25)),
                     template.format(link=link, mention="@" + rng.choice(promoted)))

    ds.truth = {"hubs": hubs, "promoted": promoted, "organic": organic, "friends": friends,
                "ring_obvious": ring, "ring_stealth": stealth, "sparse": sparse, "background": bg}

    overrides = []
    out_deg: dict[str, int] = {k: len(v) for k, v in follows.items()}
    for pid in sorted(follows):
        overrides.append({"platform_account_id": pid, "list_kind": "following", "completeness": "complete",
                          "expected_count": out_deg[pid]})
    ds.manifest = {
        "schema_version": "1.0",
        "dataset_name": "synthetic-demo",
        "platform": "x",
        "collected_at": _iso(COLLECTED_AT),
        "source_description": f"SYNTHETIC data generated by sbh.fixtures.synthetic (seed={seed}). "
                              "Every account is invented; no real people or platform data.",
        "collection_method": "synthetic",
        "relationship_coverage": {"default": "partial", "overrides": overrides},
        "notes": "Following lists are complete for accounts that have edges; followers lists are only "
                 "the observed subset (declared partial).",
    }
    return ds


# ---------------------------------------------------------------------------------------- writers

_ACCOUNT_COLS = ["platform", "platform_account_id", "observed_at", "username", "display_name",
                 "follower_count", "following_count", "post_count", "has_bio", "bio_length",
                 "has_profile_image", "has_display_name", "account_created_at", "is_verified", "is_private"]
_REL_COLS = ["platform", "source_account_id", "target_account_id", "relationship_type", "observed_at",
             "verification_status"]
_CONTENT_COLS = ["platform", "platform_content_id", "author_account_id", "published_at", "text",
                 "like_count", "reply_count", "share_count"]


def _write_csv(path: Path, cols: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def write_csv_dir(ds: SyntheticDataset, directory: str | Path) -> Path:
    d = Path(directory)
    d.mkdir(parents=True, exist_ok=True)
    (d / "manifest.json").write_text(json.dumps(ds.manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_csv(d / "accounts.csv", _ACCOUNT_COLS, ds.accounts)
    _write_csv(d / "relationships.csv", _REL_COLS, ds.relationships)
    _write_csv(d / "content.csv", _CONTENT_COLS, ds.content)
    return d


def write_json_bundle(ds: SyntheticDataset, path: str | Path) -> Path:
    def clean(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [{k: (None if v == "" else v) for k, v in r.items()} for r in rows]

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"manifest": ds.manifest, "accounts": clean(ds.accounts),
                             "relationships": clean(ds.relationships), "content": clean(ds.content)},
                            sort_keys=True), encoding="utf-8")
    return p


def make_dirty(ds: SyntheticDataset) -> SyntheticDataset:
    """Return a copy with deliberate data-quality faults, for validation and quarantine tests."""
    import copy

    d = copy.deepcopy(ds)
    base = d.accounts[0]
    d.accounts.append({**base, "platform_account_id": "bad1", "follower_count": -5})            # negative count
    d.accounts.append({**base, "platform_account_id": "bad2", "observed_at": "yesterday"})       # bad timestamp
    d.accounts.append({**base, "platform_account_id": "", "observed_at": base["observed_at"]})   # missing id
    d.accounts.append({**base, "platform_account_id": "bad3", "platform": "tiktok"})              # platform mismatch
    d.accounts.append({**base, "platform_account_id": "bad4", "observed_at": "2099-01-01T00:00:00Z"})  # future
    d.accounts.append(dict(base))                                                                  # exact duplicate
    d.accounts.append({**base, "follower_count": 7})                                               # conflicting duplicate
    e = d.relationships[0]
    d.relationships.append({**e, "target_account_id": e["source_account_id"]})                    # self-follow
    d.relationships.append({**e, "relationship_type": "blocks"})                                  # bad enum
    d.relationships.append(dict(e))                                                                # exact duplicate
    d.content.append({**d.content[0], "platform_content_id": "cbad", "published_at": ""})         # missing timestamp
    return d
