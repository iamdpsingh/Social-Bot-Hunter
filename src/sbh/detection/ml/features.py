"""Account and content feature extraction with missingness handling."""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from sbh.detection.simhash import compute_simhash, hamming_distance

CORE_FEATURE_NAMES: tuple[str, ...] = (
    "account_age_days",
    "followers_count",
    "following_count",
    "follower_following_ratio",
    "log_follower_ratio",
    "has_default_profile_image",
    "screen_name_length",
    "screen_name_digits",
    "screen_name_digit_ratio",
    "screen_name_entropy",
    "description_length",
    "description_has_url",
    "description_uppercase_ratio",
    "statuses_count",
    "post_frequency_per_day",
    "mean_inter_post_time_sec",
    "std_inter_post_time_sec",
    "hourly_entropy",
    "simhash_max_cluster_size",
    "simhash_duplicate_ratio",
    "url_post_ratio",
    "mention_post_ratio",
)

INDICATOR_FEATURE_NAMES: tuple[str, ...] = tuple(f"is_missing_{f}" for f in CORE_FEATURE_NAMES)
ALL_FEATURE_NAMES: tuple[str, ...] = CORE_FEATURE_NAMES + INDICATOR_FEATURE_NAMES


@dataclass
class AccountFeatureVector:
    """Extracted raw feature values for an account, with optional None for missing."""

    account_id: str
    features: dict[str, float | None] = field(default_factory=dict)
    extracted_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def get(self, name: str, default: float | None = None) -> float | None:
        return self.features.get(name, default)


def calculate_shannon_entropy(text: str) -> float:
    """Compute Shannon entropy in bits for an input string."""
    if not text:
        return 0.0
    length = len(text)
    counts = Counter(text)
    entropy = 0.0
    for count in counts.values():
        p = count / length
        entropy -= p * math.log2(p)
    return round(entropy, 4)


def calculate_hourly_entropy(timestamps: list[datetime]) -> float:
    """Compute normalized entropy of activity across 24 hours of the day [0.0, 1.0]."""
    if not timestamps:
        return 0.0
    hours = [dt.hour for dt in timestamps]
    counts = Counter(hours)
    n = len(timestamps)
    entropy = 0.0
    for count in counts.values():
        p = count / n
        entropy -= p * math.log2(p)
    # Normalized by max entropy log2(24) ~ 4.58496 bits
    max_entropy = math.log2(24)
    normalized = entropy / max_entropy if max_entropy > 0 else 0.0
    return round(min(1.0, max(0.0, normalized)), 4)


def calculate_inter_post_intervals(timestamps: list[datetime]) -> tuple[float | None, float | None]:
    """Calculate mean and standard deviation of inter-post arrival times in seconds."""
    if len(timestamps) < 2:
        return None, None
    sorted_ts = sorted(timestamps)
    intervals: list[float] = []
    for i in range(1, len(sorted_ts)):
        delta = (sorted_ts[i] - sorted_ts[i - 1]).total_seconds()
        if delta >= 0:
            intervals.append(delta)
    if not intervals:
        return None, None
    mean_val = sum(intervals) / len(intervals)
    variance = sum((x - mean_val) ** 2 for x in intervals) / len(intervals)
    std_val = math.sqrt(variance)
    return round(mean_val, 2), round(std_val, 2)


def calculate_simhash_repetition(texts: list[str], max_hamming_dist: int = 3) -> tuple[int, float]:
    """Identify near-duplicate content clusters using 64-bit SimHash.

    Returns:
        (max_cluster_size, duplicate_ratio)
    """
    non_empty = [t.strip() for t in texts if t and t.strip()]
    if not non_empty:
        return 0, 0.0
    if len(non_empty) == 1:
        return 1, 0.0

    hashes = [compute_simhash(t) for t in non_empty]
    n = len(hashes)
    visited = [False] * n
    clusters: list[list[int]] = []

    for i in range(n):
        if visited[i]:
            continue
        cluster = [i]
        visited[i] = True
        for j in range(i + 1, n):
            if not visited[j] and hamming_distance(hashes[i], hashes[j]) <= max_hamming_dist:
                cluster.append(j)
                visited[j] = True
        clusters.append(cluster)

    max_cluster = max(len(c) for c in clusters)
    # Duplicate items are any items beyond the first in clusters of size > 1
    dup_items = sum(len(c) - 1 for c in clusters if len(c) > 1)
    dup_ratio = round(dup_items / n, 4)
    return max_cluster, dup_ratio


def extract_profile_features(account: dict[str, Any], reference_time: datetime | None = None) -> dict[str, float | None]:
    """Extract numerical profile features from account dictionary."""
    ref = reference_time or datetime.now(UTC)
    feats: dict[str, float | None] = {}

    # Account age
    created_at = account.get("created_at")
    if isinstance(created_at, datetime):
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=UTC)
        age_days = (ref - created_at).total_seconds() / 86400.0
        feats["account_age_days"] = max(0.0, round(age_days, 2))
    else:
        feats["account_age_days"] = None

    # Followers / Following
    followers = account.get("followers_count")
    following = account.get("following_count")
    feats["followers_count"] = float(followers) if followers is not None else None
    feats["following_count"] = float(following) if following is not None else None

    if feats["followers_count"] is not None and feats["following_count"] is not None:
        denom = max(1.0, feats["following_count"])
        ratio = feats["followers_count"] / denom
        feats["follower_following_ratio"] = round(ratio, 4)
        feats["log_follower_ratio"] = round(math.log10(ratio + 0.001), 4)
    else:
        feats["follower_following_ratio"] = None
        feats["log_follower_ratio"] = None

    # Default profile image
    default_img = account.get("default_profile_image")
    if default_img is not None:
        feats["has_default_profile_image"] = 1.0 if default_img else 0.0
    else:
        feats["has_default_profile_image"] = None

    # Screen name
    username = str(account.get("username") or account.get("screen_name") or "")
    if username:
        feats["screen_name_length"] = float(len(username))
        digits = sum(1 for c in username if c.isdigit())
        feats["screen_name_digits"] = float(digits)
        feats["screen_name_digit_ratio"] = round(digits / len(username), 4)
        feats["screen_name_entropy"] = calculate_shannon_entropy(username)
    else:
        feats["screen_name_length"] = None
        feats["screen_name_digits"] = None
        feats["screen_name_digit_ratio"] = None
        feats["screen_name_entropy"] = None

    # Description
    desc = str(account.get("description") or "")
    feats["description_length"] = float(len(desc))
    feats["description_has_url"] = 1.0 if ("http://" in desc or "https://" in desc) else 0.0
    if desc:
        alpha_chars = [c for c in desc if c.isalpha()]
        upper_chars = [c for c in alpha_chars if c.isupper()]
        feats["description_uppercase_ratio"] = round(len(upper_chars) / len(alpha_chars), 4) if alpha_chars else 0.0
    else:
        feats["description_uppercase_ratio"] = 0.0

    statuses = account.get("statuses_count") or account.get("post_count")
    feats["statuses_count"] = float(statuses) if statuses is not None else None

    return feats


def extract_content_features(contents: list[dict[str, Any]], account_age_days: float | None = None) -> dict[str, float | None]:
    """Extract behavioral and textual features from an account's recent content items."""
    feats: dict[str, float | None] = {}
    if not contents:
        feats["post_frequency_per_day"] = None
        feats["mean_inter_post_time_sec"] = None
        feats["std_inter_post_time_sec"] = None
        feats["hourly_entropy"] = None
        feats["simhash_max_cluster_size"] = None
        feats["simhash_duplicate_ratio"] = None
        feats["url_post_ratio"] = None
        feats["mention_post_ratio"] = None
        return feats

    n = len(contents)
    # Timestamps
    timestamps: list[datetime] = []
    for c in contents:
        ts = c.get("created_at") or c.get("posted_at")
        if isinstance(ts, datetime):
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=UTC)
            timestamps.append(ts)
        elif isinstance(ts, str):
            try:
                parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                timestamps.append(parsed)
            except ValueError:
                pass

    if timestamps:
        feats["hourly_entropy"] = calculate_hourly_entropy(timestamps)
        mean_sec, std_sec = calculate_inter_post_intervals(timestamps)
        feats["mean_inter_post_time_sec"] = mean_sec
        feats["std_inter_post_time_sec"] = std_sec

        if account_age_days and account_age_days > 0:
            feats["post_frequency_per_day"] = round(n / account_age_days, 4)
        else:
            time_span_days = max(1.0 / 86400.0, (max(timestamps) - min(timestamps)).total_seconds() / 86400.0)
            feats["post_frequency_per_day"] = round(n / time_span_days, 4)
    else:
        feats["hourly_entropy"] = None
        feats["mean_inter_post_time_sec"] = None
        feats["std_inter_post_time_sec"] = None
        feats["post_frequency_per_day"] = None

    # Text SimHash
    texts = [str(c.get("text") or c.get("content") or "") for c in contents]
    max_c, dup_r = calculate_simhash_repetition(texts)
    feats["simhash_max_cluster_size"] = float(max_c)
    feats["simhash_duplicate_ratio"] = dup_r

    # Content URLs and mentions
    url_posts = sum(1 for t in texts if "http://" in t or "https://" in t)
    mention_posts = sum(1 for t in texts if "@" in t)
    feats["url_post_ratio"] = round(url_posts / n, 4)
    feats["mention_post_ratio"] = round(mention_posts / n, 4)

    return feats


class AccountFeatureExtractor:
    """Unified extractor parsing account dictionary and content list into AccountFeatureVector."""

    def __init__(self, reference_time: datetime | None = None) -> None:
        self.reference_time = reference_time

    def extract(self, account: dict[str, Any], contents: list[dict[str, Any]] | None = None) -> AccountFeatureVector:
        acc_id = str(account.get("account_id") or account.get("id") or account.get("username") or "unknown")
        profile_feats = extract_profile_features(account, self.reference_time)
        content_feats = extract_content_features(contents or [], profile_feats.get("account_age_days"))

        combined = {**profile_feats, **content_feats}
        # Enforce all core feature keys present
        final_feats: dict[str, float | None] = {}
        for name in CORE_FEATURE_NAMES:
            final_feats[name] = combined.get(name)

        return AccountFeatureVector(account_id=acc_id, features=final_feats)


class FeatureImputer:
    """Imputes missing numerical values with learned medians and appends missingness indicator flags."""

    def __init__(self) -> None:
        self.medians: dict[str, float] = {}
        self.is_fitted: bool = False

    def fit(self, vectors: list[AccountFeatureVector]) -> FeatureImputer:
        """Compute median values across non-None feature observations."""
        for name in CORE_FEATURE_NAMES:
            values = [v.features[name] for v in vectors if v.features.get(name) is not None]
            if values:
                sorted_vals = sorted(v for v in values if v is not None)
                n = len(sorted_vals)
                mid = n // 2
                median_val = (sorted_vals[mid] if n % 2 != 0 else (sorted_vals[mid - 1] + sorted_vals[mid]) / 2.0)
                self.medians[name] = float(median_val)
            else:
                self.medians[name] = 0.0
        self.is_fitted = True
        return self

    def transform(self, vector: AccountFeatureVector) -> list[float]:
        """Transform vector into a 44-dimensional float list [core_imputed, indicators]."""
        if not self.is_fitted:
            raise ValueError("FeatureImputer must be fitted before calling transform.")

        core_vals: list[float] = []
        indicators: list[float] = []

        for name in CORE_FEATURE_NAMES:
            val = vector.features.get(name)
            if val is None:
                core_vals.append(self.medians.get(name, 0.0))
                indicators.append(1.0)
            else:
                core_vals.append(float(val))
                indicators.append(0.0)

        return core_vals + indicators

    def transform_batch(self, vectors: list[AccountFeatureVector]) -> list[list[float]]:
        return [self.transform(v) for v in vectors]


class MLFeaturePipeline:
    """End-to-end extraction and imputation pipeline."""

    def __init__(self, imputer: FeatureImputer | None = None) -> None:
        self.extractor = AccountFeatureExtractor()
        self.imputer = imputer or FeatureImputer()

    def fit(self, accounts: list[dict[str, Any]], contents_map: dict[str, list[dict[str, Any]]] | None = None) -> MLFeaturePipeline:
        contents_map = contents_map or {}
        vectors = [
            self.extractor.extract(acc, contents_map.get(str(acc.get("account_id") or acc.get("username") or "")))
            for acc in accounts
        ]
        self.imputer.fit(vectors)
        return self

    def transform_one(self, account: dict[str, Any], contents: list[dict[str, Any]] | None = None) -> list[float]:
        vec = self.extractor.extract(account, contents)
        return self.imputer.transform(vec)


def extract_feature_matrix(
    accounts: list[dict[str, Any]],
    contents_map: dict[str, list[dict[str, Any]]] | None = None,
    imputer: FeatureImputer | None = None,
) -> tuple[list[list[float]], FeatureImputer]:
    """Convenience function to extract and impute features for a batch of accounts."""
    contents_map = contents_map or {}
    extractor = AccountFeatureExtractor()
    vectors = [
        extractor.extract(acc, contents_map.get(str(acc.get("account_id") or acc.get("username") or "")))
        for acc in accounts
    ]
    if imputer is None:
        imputer = FeatureImputer().fit(vectors)
    matrix = imputer.transform_batch(vectors)
    return matrix, imputer
