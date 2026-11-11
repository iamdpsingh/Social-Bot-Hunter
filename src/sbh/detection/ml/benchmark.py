"""Benchmark dataset generator for ground truth bot and benign profiles."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any


@dataclass
class BenchmarkDataset:
    """Synthetic benchmark dataset with known ground-truth labels and campaign clusters."""

    accounts: list[dict[str, Any]]
    contents_map: dict[str, list[dict[str, Any]]]
    labels: list[int]  # 0 = benign, 1 = bot
    campaign_groups: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


def generate_benchmark_dataset(
    n_benign: int = 50,
    n_bots: int = 50,
    n_campaigns: int = 5,
    random_seed: int = 42,
) -> BenchmarkDataset:
    """Generate balanced, realistic ground-truth benchmark dataset."""
    import random
    rng = random.Random(random_seed)
    now = datetime(2026, 11, 10, 12, 0, 0, tzinfo=UTC)

    accounts: list[dict[str, Any]] = []
    contents_map: dict[str, list[dict[str, Any]]] = {}
    labels: list[int] = []
    campaign_groups: list[str] = []

    # 1. Benign accounts
    for i in range(n_benign):
        acc_id = f"benign_{i:03d}"
        created_days_ago = rng.randint(300, 2000)
        followers = rng.randint(50, 5000)
        following = rng.randint(50, 2000)
        acc = {
            "account_id": acc_id,
            "username": f"organic_user_{i}",
            "created_at": now - timedelta(days=created_days_ago),
            "followers_count": followers,
            "following_count": following,
            "default_profile_image": False,
            "description": f"Personal thoughts and hobbies #{i}",
            "statuses_count": rng.randint(20, 500),
        }
        accounts.append(acc)
        labels.append(0)
        campaign_groups.append(f"benign_cluster_{i % 10}")

        # Organic posts: spread over days, diverse text
        posts = []
        for p in range(5):
            posts.append({
                "text": f"Enjoying coffee and coding project item {p} on day {i}",
                "created_at": now - timedelta(days=rng.randint(1, 60), hours=rng.randint(8, 22)),
            })
        contents_map[acc_id] = posts

    # 2. Coordinated Bot accounts
    for i in range(n_bots):
        acc_id = f"bot_{i:03d}"
        camp_id = f"campaign_{i % n_campaigns}"
        created_days_ago = rng.randint(1, 30)
        followers = rng.randint(0, 50)
        following = rng.randint(500, 2500)
        digits = f"{rng.randint(1000, 9999)}"
        acc = {
            "account_id": acc_id,
            "username": f"crypto_alert_{digits}",
            "created_at": now - timedelta(days=created_days_ago),
            "followers_count": followers,
            "following_count": following,
            "default_profile_image": rng.choice([True, False]),
            "description": "JOIN TELEGRAM FOR 100X CRYPTO PUMP https://scam.xyz",
            "statuses_count": rng.randint(100, 1000),
        }
        accounts.append(acc)
        labels.append(1)
        campaign_groups.append(camp_id)

        # Bot posts: repetitive spam, concentrated hours
        posts = []
        for p in range(5):
            posts.append({
                "text": f"FREE AIRDROP ALERT: Claim now at https://scam.xyz/claim #{camp_id}",
                "created_at": now - timedelta(hours=3, minutes=p * 2),
            })
        contents_map[acc_id] = posts

    return BenchmarkDataset(
        accounts=accounts,
        contents_map=contents_map,
        labels=labels,
        campaign_groups=campaign_groups,
        metadata={
            "n_benign": n_benign,
            "n_bots": n_bots,
            "n_campaigns": n_campaigns,
            "created_at": now.isoformat(),
        },
    )
