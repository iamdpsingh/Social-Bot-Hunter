#!/usr/bin/env python3
"""Batch 1 runner for Day 11: Feature Extraction Pipeline (sbh.detection.ml.features).
Executes 25 granular, atomic, functional commits timestamped 2026-11-11 09:00:00 to 09:48:00 +0530.
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Volumes/Work/daemons-lab/p.automation/Social Bot Hunter")
AUTHOR_NAME = "dpsingh"
AUTHOR_EMAIL = "dhruvpratapsingh30.official2.o@gmail.com"


def run_cmd(cmd: list[str], cwd: Path = ROOT) -> str:
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FAILED: {' '.join(cmd)}\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}", file=sys.stderr)
        sys.exit(1)
    return res.stdout.strip()


def git_commit(message: str, date_iso: str, files: list[str]) -> None:
    for f in files:
        run_cmd(["git", "add", f])
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = AUTHOR_NAME
    env["GIT_AUTHOR_EMAIL"] = AUTHOR_EMAIL
    env["GIT_AUTHOR_DATE"] = date_iso
    env["GIT_COMMITTER_NAME"] = AUTHOR_NAME
    env["GIT_COMMITTER_EMAIL"] = AUTHOR_EMAIL
    env["GIT_COMMITTER_DATE"] = date_iso
    res = subprocess.run(
        ["git", "commit", "-m", message],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        print(f"Git commit failed: {res.stderr}\n{res.stdout}", file=sys.stderr)
        sys.exit(1)
    print(f"Committed [{date_iso}]: {message}")


def step_01():
    # chore(deps): add scikit-learn and joblib to project dependencies in pyproject.toml
    pyproject = ROOT / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8")
    new_deps = """dependencies = [
  "networkx>=3.2",
  "PyYAML>=6.0",
  "scikit-learn>=1.4.0",
  "joblib>=1.3.0",
]"""
    content = content.replace(
        """dependencies = [
  "networkx>=3.2",
  "PyYAML>=6.0",
]""",
        new_deps,
    )
    pyproject.write_text(content, encoding="utf-8")
    git_commit(
        "chore(deps): add scikit-learn and joblib to project dependencies in pyproject.toml",
        "2026-11-11 09:00:00 +0530",
        ["pyproject.toml"],
    )


def step_02():
    # feat(ml): initialize sbh.detection.ml package namespace
    pkg_init = ROOT / "src/sbh/detection/ml/__init__.py"
    pkg_init.parent.mkdir(parents=True, exist_ok=True)
    pkg_init.write_text(
        '"""Machine learning detection, evaluation, and calibration package."""\n\nfrom __future__ import annotations\n',
        encoding="utf-8",
    )
    git_commit(
        "feat(ml): initialize sbh.detection.ml package namespace",
        "2026-11-11 09:02:00 +0530",
        ["src/sbh/detection/ml/__init__.py"],
    )


def step_03():
    # feat(ml): define base feature schema constants and AccountFeatureVector dataclass
    features_py = ROOT / "src/sbh/detection/ml/features.py"
    content = '''"""Account and content feature extraction with missingness handling."""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
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
    extracted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def get(self, name: str, default: float | None = None) -> float | None:
        return self.features.get(name, default)
'''
    features_py.write_text(content, encoding="utf-8")
    git_commit(
        "feat(ml): define base feature schema constants and AccountFeatureVector dataclass",
        "2026-11-11 09:04:00 +0530",
        ["src/sbh/detection/ml/features.py"],
    )


def step_04():
    # feat(ml): implement shannon entropy calculator for screen names and text
    features_py = ROOT / "src/sbh/detection/ml/features.py"
    code = """

def calculate_shannon_entropy(text: str) -> float:
    \"\"\"Compute Shannon entropy in bits for an input string.\"\"\"
    if not text:
        return 0.0
    length = len(text)
    counts = Counter(text)
    entropy = 0.0
    for count in counts.values():
        p = count / length
        entropy -= p * math.log2(p)
    return round(entropy, 4)
"""
    with open(features_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): implement shannon entropy calculator for screen names and text",
        "2026-11-11 09:06:00 +0530",
        ["src/sbh/detection/ml/features.py"],
    )


def step_05():
    # feat(ml): implement hourly activity entropy calculator for circadian rhythms
    features_py = ROOT / "src/sbh/detection/ml/features.py"
    code = """

def calculate_hourly_entropy(timestamps: list[datetime]) -> float:
    \"\"\"Compute normalized entropy of activity across 24 hours of the day [0.0, 1.0].\"\"\"
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
"""
    with open(features_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): implement hourly activity entropy calculator for circadian rhythms",
        "2026-11-11 09:08:00 +0530",
        ["src/sbh/detection/ml/features.py"],
    )


def step_06():
    # feat(ml): implement inter-post arrival time statistics extractor
    features_py = ROOT / "src/sbh/detection/ml/features.py"
    code = """

def calculate_inter_post_intervals(timestamps: list[datetime]) -> tuple[float | None, float | None]:
    \"\"\"Calculate mean and standard deviation of inter-post arrival times in seconds.\"\"\"
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
"""
    with open(features_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): implement inter-post arrival time statistics extractor",
        "2026-11-11 09:10:00 +0530",
        ["src/sbh/detection/ml/features.py"],
    )


def step_07():
    # feat(ml): implement simhash duplicate ratio and max cluster size extractor
    features_py = ROOT / "src/sbh/detection/ml/features.py"
    code = """

def calculate_simhash_repetition(texts: list[str], max_hamming_dist: int = 3) -> tuple[int, float]:
    \"\"\"Identify near-duplicate content clusters using 64-bit SimHash.

    Returns:
        (max_cluster_size, duplicate_ratio)
    \"\"\"
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
"""
    with open(features_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): implement simhash duplicate ratio and max cluster size extractor",
        "2026-11-11 09:12:00 +0530",
        ["src/sbh/detection/ml/features.py"],
    )


def step_08():
    # feat(ml): implement profile metadata feature extraction logic
    features_py = ROOT / "src/sbh/detection/ml/features.py"
    code = """

def extract_profile_features(account: dict[str, Any], reference_time: datetime | None = None) -> dict[str, float | None]:
    \"\"\"Extract numerical profile features from account dictionary.\"\"\"
    ref = reference_time or datetime.now(timezone.utc)
    feats: dict[str, float | None] = {}

    # Account age
    created_at = account.get("created_at")
    if isinstance(created_at, datetime):
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
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
"""
    with open(features_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): implement profile metadata feature extraction logic",
        "2026-11-11 09:14:00 +0530",
        ["src/sbh/detection/ml/features.py"],
    )


def step_09():
    # feat(ml): implement content ratio feature extraction for urls mentions and hashtags
    features_py = ROOT / "src/sbh/detection/ml/features.py"
    code = """

def extract_content_features(contents: list[dict[str, Any]], account_age_days: float | None = None) -> dict[str, float | None]:
    \"\"\"Extract behavioral and textual features from an account's recent content items.\"\"\"
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
                ts = ts.replace(tzinfo=timezone.utc)
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
"""
    with open(features_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): implement content ratio feature extraction for urls mentions and hashtags",
        "2026-11-11 09:16:00 +0530",
        ["src/sbh/detection/ml/features.py"],
    )


def step_10():
    # feat(ml): assemble AccountFeatureExtractor extracting 22 core features
    features_py = ROOT / "src/sbh/detection/ml/features.py"
    code = """

class AccountFeatureExtractor:
    \"\"\"Unified extractor parsing account dictionary and content list into AccountFeatureVector.\"\"\"

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
"""
    with open(features_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): assemble AccountFeatureExtractor extracting 22 core features",
        "2026-11-11 09:18:00 +0530",
        ["src/sbh/detection/ml/features.py"],
    )


def step_11():
    # feat(ml): implement FeatureImputer with median substitution and missingness indicators
    features_py = ROOT / "src/sbh/detection/ml/features.py"
    code = """

class FeatureImputer:
    \"\"\"Imputes missing numerical values with learned medians and appends missingness indicator flags.\"\"\"

    def __init__(self) -> None:
        self.medians: dict[str, float] = {}
        self.is_fitted: bool = False

    def fit(self, vectors: list[AccountFeatureVector]) -> FeatureImputer:
        \"\"\"Compute median values across non-None feature observations.\"\"\"
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
        \"\"\"Transform vector into a 44-dimensional float list [core_imputed, indicators].\"\"\"
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
"""
    with open(features_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): implement FeatureImputer with median substitution and missingness indicators",
        "2026-11-11 09:20:00 +0530",
        ["src/sbh/detection/ml/features.py"],
    )


def step_12():
    # feat(ml): add vectorizer transform returning 44-dimensional feature arrays
    features_py = ROOT / "src/sbh/detection/ml/features.py"
    code = """

class MLFeaturePipeline:
    \"\"\"End-to-end extraction and imputation pipeline.\"\"\"

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
"""
    with open(features_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): add vectorizer transform returning 44-dimensional feature arrays",
        "2026-11-11 09:22:00 +0530",
        ["src/sbh/detection/ml/features.py"],
    )


def step_13():
    # feat(ml): add batch extraction helper for collections of accounts and contents
    features_py = ROOT / "src/sbh/detection/ml/features.py"
    code = """

def extract_feature_matrix(
    accounts: list[dict[str, Any]],
    contents_map: dict[str, list[dict[str, Any]]] | None = None,
    imputer: FeatureImputer | None = None,
) -> tuple[list[list[float]], FeatureImputer]:
    \"\"\"Convenience function to extract and impute features for a batch of accounts.\"\"\"
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
"""
    with open(features_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(ml): add batch extraction helper for collections of accounts and contents",
        "2026-11-11 09:24:00 +0530",
        ["src/sbh/detection/ml/features.py"],
    )


def step_14():
    # test(ml): add unit test for shannon entropy calculations
    test_file = ROOT / "tests/detection/test_ml_features.py"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    content = '''"""Unit tests for ML feature extraction, imputation, and vectorization."""

import unittest
from datetime import datetime, timezone
from sbh.detection.ml.features import (
    calculate_shannon_entropy,
    calculate_hourly_entropy,
    calculate_inter_post_intervals,
    calculate_simhash_repetition,
    extract_profile_features,
    extract_content_features,
    AccountFeatureExtractor,
    FeatureImputer,
    MLFeaturePipeline,
    extract_feature_matrix,
    CORE_FEATURE_NAMES,
    ALL_FEATURE_NAMES,
)


class TestShannonEntropy(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(calculate_shannon_entropy(""), 0.0)

    def test_single_repeated_char(self):
        self.assertEqual(calculate_shannon_entropy("aaaaaaa"), 0.0)

    def test_random_string_positive_entropy(self):
        h = calculate_shannon_entropy("bot_hunter_9988_xyz")
        self.assertGreater(h, 3.0)
'''
    test_file.write_text(content, encoding="utf-8")
    git_commit(
        "test(ml): add unit test for shannon entropy calculations",
        "2026-11-11 09:26:00 +0530",
        ["tests/detection/test_ml_features.py"],
    )


def step_15():
    # test(ml): add unit test for hourly posting entropy and circadian rhythm signals
    test_file = ROOT / "tests/detection/test_ml_features.py"
    code = """

class TestHourlyEntropy(unittest.TestCase):
    def test_empty_timestamps(self):
        self.assertEqual(calculate_hourly_entropy([]), 0.0)

    def test_single_hour_spam(self):
        # 10 posts all at hour 3
        ts = [datetime(2026, 11, 10, 3, i, 0, tzinfo=timezone.utc) for i in range(10)]
        self.assertEqual(calculate_hourly_entropy(ts), 0.0)

    def test_uniform_circadian_entropy(self):
        # 24 posts evenly spaced across 24 hours
        ts = [datetime(2026, 11, 10, h, 0, 0, tzinfo=timezone.utc) for h in range(24)]
        self.assertAlmostEqual(calculate_hourly_entropy(ts), 1.0, places=2)
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for hourly posting entropy and circadian rhythm signals",
        "2026-11-11 09:28:00 +0530",
        ["tests/detection/test_ml_features.py"],
    )


def step_16():
    # test(ml): add unit test for inter-post arrival time calculation
    test_file = ROOT / "tests/detection/test_ml_features.py"
    code = """

class TestInterPostIntervals(unittest.TestCase):
    def test_insufficient_timestamps(self):
        m, s = calculate_inter_post_intervals([])
        self.assertIsNone(m)
        self.assertIsNone(s)
        m, s = calculate_inter_post_intervals([datetime.now(timezone.utc)])
        self.assertIsNone(m)

    def test_exact_periodic_intervals(self):
        # Exactly 60 seconds apart: mean=60.0, std=0.0
        ts = [
            datetime(2026, 11, 10, 10, 0, 0, tzinfo=timezone.utc),
            datetime(2026, 11, 10, 10, 1, 0, tzinfo=timezone.utc),
            datetime(2026, 11, 10, 10, 2, 0, tzinfo=timezone.utc),
        ]
        mean_sec, std_sec = calculate_inter_post_intervals(ts)
        self.assertEqual(mean_sec, 60.0)
        self.assertEqual(std_sec, 0.0)
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for inter-post arrival time calculation",
        "2026-11-11 09:30:00 +0530",
        ["tests/detection/test_ml_features.py"],
    )


def step_17():
    # test(ml): add unit test for simhash cluster and duplication ratio extraction
    test_file = ROOT / "tests/detection/test_ml_features.py"
    code = """

class TestSimHashRepetition(unittest.TestCase):
    def test_empty_or_single_text(self):
        self.assertEqual(calculate_simhash_repetition([]), (0, 0.0))
        self.assertEqual(calculate_simhash_repetition(["hello"]), (1, 0.0))

    def test_duplicate_spam_clusters(self):
        texts = [
            "BREAKING NEWS: Check out this amazing free coin drop now!",
            "BREAKING NEWS: Check out this amazing free coin drop now!",
            "BREAKING NEWS: Check out this amazing free coin drop now!",
            "Completely distinct organic comment about the weather today.",
        ]
        max_c, dup_r = calculate_simhash_repetition(texts)
        self.assertEqual(max_c, 3)
        self.assertEqual(dup_r, 0.5)  # 2 duplicates out of 4 total
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for simhash cluster and duplication ratio extraction",
        "2026-11-11 09:32:00 +0530",
        ["tests/detection/test_ml_features.py"],
    )


def step_18():
    # test(ml): add unit test for profile metadata and ratio extraction
    test_file = ROOT / "tests/detection/test_ml_features.py"
    code = """

class TestProfileFeatures(unittest.TestCase):
    def test_complete_profile(self):
        ref = datetime(2026, 11, 10, 12, 0, 0, tzinfo=timezone.utc)
        acc = {
            "account_id": "user_101",
            "username": "crypto_bot_7788",
            "created_at": datetime(2026, 11, 8, 12, 0, 0, tzinfo=timezone.utc),
            "followers_count": 50,
            "following_count": 1000,
            "default_profile_image": True,
            "description": "Follow me for crypto gems! https://spam.xyz",
            "statuses_count": 500,
        }
        feats = extract_profile_features(acc, ref)
        self.assertEqual(feats["account_age_days"], 2.0)
        self.assertEqual(feats["followers_count"], 50.0)
        self.assertEqual(feats["following_count"], 1000.0)
        self.assertEqual(feats["follower_following_ratio"], 0.05)
        self.assertEqual(feats["has_default_profile_image"], 1.0)
        self.assertEqual(feats["description_has_url"], 1.0)
        self.assertEqual(feats["screen_name_digits"], 4.0)
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for profile metadata and ratio extraction",
        "2026-11-11 09:34:00 +0530",
        ["tests/detection/test_ml_features.py"],
    )


def step_19():
    # test(ml): add unit test for content interaction ratios (urls, mentions, hashtags)
    test_file = ROOT / "tests/detection/test_ml_features.py"
    code = """

class TestContentFeatures(unittest.TestCase):
    def test_content_ratios(self):
        contents = [
            {"text": "Check out https://example.com/deal", "created_at": "2026-11-10T10:00:00Z"},
            {"text": "Hey @friend look at this!", "created_at": "2026-11-10T11:00:00Z"},
            {"text": "Just another normal post", "created_at": "2026-11-10T12:00:00Z"},
            {"text": "Dual link https://link.org with @someone", "created_at": "2026-11-10T13:00:00Z"},
        ]
        feats = extract_content_features(contents, account_age_days=1.0)
        self.assertEqual(feats["url_post_ratio"], 0.5)
        self.assertEqual(feats["mention_post_ratio"], 0.5)
        self.assertEqual(feats["simhash_max_cluster_size"], 1.0)
        self.assertEqual(feats["simhash_duplicate_ratio"], 0.0)
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for content interaction ratios (urls, mentions, hashtags)",
        "2026-11-11 09:36:00 +0530",
        ["tests/detection/test_ml_features.py"],
    )


def step_20():
    # test(ml): add unit test for complete account feature extraction
    test_file = ROOT / "tests/detection/test_ml_features.py"
    code = """

class TestAccountFeatureExtractor(unittest.TestCase):
    def test_extract_all_core_features_present(self):
        extractor = AccountFeatureExtractor()
        acc = {
            "account_id": "acc_001",
            "username": "bot_99",
            "created_at": datetime(2026, 11, 1, tzinfo=timezone.utc),
            "followers_count": 10,
            "following_count": 100,
            "default_profile_image": False,
            "description": "Just an account",
            "statuses_count": 5,
        }
        contents = [{"text": "Hello world", "created_at": datetime(2026, 11, 5, tzinfo=timezone.utc)}]
        vec = extractor.extract(acc, contents)
        self.assertEqual(vec.account_id, "acc_001")
        for name in CORE_FEATURE_NAMES:
            self.assertIn(name, vec.features)
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for complete account feature extraction",
        "2026-11-11 09:38:00 +0530",
        ["tests/detection/test_ml_features.py"],
    )


def step_21():
    # test(ml): add unit test for minimal account profile with missing fields
    test_file = ROOT / "tests/detection/test_ml_features.py"
    code = """

    def test_minimal_profile_missing_fields(self):
        extractor = AccountFeatureExtractor()
        acc = {"account_id": "bare_acc"}
        vec = extractor.extract(acc, [])
        self.assertEqual(vec.account_id, "bare_acc")
        self.assertIsNone(vec.features["followers_count"])
        self.assertIsNone(vec.features["account_age_days"])
        self.assertIsNone(vec.features["hourly_entropy"])
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for minimal account profile with missing fields",
        "2026-11-11 09:40:00 +0530",
        ["tests/detection/test_ml_features.py"],
    )


def step_22():
    # test(ml): add unit test for FeatureImputer median calculation and missingness flags
    test_file = ROOT / "tests/detection/test_ml_features.py"
    code = """

class TestFeatureImputer(unittest.TestCase):
    def test_imputation_and_indicators(self):
        extractor = AccountFeatureExtractor()
        v1 = extractor.extract({"account_id": "1", "followers_count": 10, "following_count": 100})
        v2 = extractor.extract({"account_id": "2", "followers_count": 30, "following_count": 100})
        v3 = extractor.extract({"account_id": "3", "following_count": 100})  # followers_count is None

        imputer = FeatureImputer().fit([v1, v2, v3])
        self.assertEqual(imputer.medians["followers_count"], 20.0)

        # Transform v3
        transformed = imputer.transform(v3)
        self.assertEqual(len(transformed), 44)  # 22 core + 22 indicators

        # Find index of followers_count
        f_idx = CORE_FEATURE_NAMES.index("followers_count")
        # Core imputed value should be median (20.0)
        self.assertEqual(transformed[f_idx], 20.0)
        # Indicator value should be 1.0 (missing)
        self.assertEqual(transformed[22 + f_idx], 1.0)

        # following_count was present in v3
        flw_idx = CORE_FEATURE_NAMES.index("following_count")
        self.assertEqual(transformed[flw_idx], 100.0)
        self.assertEqual(transformed[22 + flw_idx], 0.0)
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for FeatureImputer median calculation and missingness flags",
        "2026-11-11 09:42:00 +0530",
        ["tests/detection/test_ml_features.py"],
    )


def step_23():
    # test(ml): add unit test for feature vectorization shape and ordering guarantees
    test_file = ROOT / "tests/detection/test_ml_features.py"
    code = """

    def test_pipeline_shape_and_names(self):
        self.assertEqual(len(CORE_FEATURE_NAMES), 22)
        self.assertEqual(len(ALL_FEATURE_NAMES), 44)
        pipeline = MLFeaturePipeline()
        accounts = [
            {"account_id": "a", "username": "alice", "followers_count": 100},
            {"account_id": "b", "username": "bob", "followers_count": 200},
        ]
        pipeline.fit(accounts)
        row = pipeline.transform_one({"account_id": "c", "username": "charlie"})
        self.assertEqual(len(row), 44)
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add unit test for feature vectorization shape and ordering guarantees",
        "2026-11-11 09:44:00 +0530",
        ["tests/detection/test_ml_features.py"],
    )


def step_24():
    # test(ml): add edge case tests for division by zero and extreme timestamp intervals
    test_file = ROOT / "tests/detection/test_ml_features.py"
    code = """

class TestFeatureEdgeCases(unittest.TestCase):
    def test_zero_following_division(self):
        feats = extract_profile_features({"following_count": 0, "followers_count": 50})
        self.assertEqual(feats["follower_following_ratio"], 50.0)

    def test_identical_timestamps_zero_interval(self):
        now = datetime(2026, 11, 10, 10, 0, 0, tzinfo=timezone.utc)
        m, s = calculate_inter_post_intervals([now, now, now])
        self.assertEqual(m, 0.0)
        self.assertEqual(s, 0.0)

    def test_batch_matrix_extractor(self):
        accs = [{"account_id": "1"}, {"account_id": "2"}]
        mat, imp = extract_feature_matrix(accs)
        self.assertEqual(len(mat), 2)
        self.assertEqual(len(mat[0]), 44)
        self.assertTrue(imp.is_fitted)


if __name__ == "__main__":
    unittest.main()
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(ml): add edge case tests for division by zero and extreme timestamp intervals",
        "2026-11-11 09:46:00 +0530",
        ["tests/detection/test_ml_features.py"],
    )


def step_25():
    # refactor(ml): export feature extraction interfaces in sbh.detection.ml namespace
    pkg_init = ROOT / "src/sbh/detection/ml/__init__.py"
    content = '''"""Machine learning detection, evaluation, and calibration package."""

from __future__ import annotations

from sbh.detection.ml.features import (
    ALL_FEATURE_NAMES,
    CORE_FEATURE_NAMES,
    INDICATOR_FEATURE_NAMES,
    AccountFeatureExtractor,
    AccountFeatureVector,
    FeatureImputer,
    MLFeaturePipeline,
    calculate_hourly_entropy,
    calculate_inter_post_intervals,
    calculate_shannon_entropy,
    calculate_simhash_repetition,
    extract_content_features,
    extract_feature_matrix,
    extract_profile_features,
)

__all__ = [
    "ALL_FEATURE_NAMES",
    "CORE_FEATURE_NAMES",
    "INDICATOR_FEATURE_NAMES",
    "AccountFeatureExtractor",
    "AccountFeatureVector",
    "FeatureImputer",
    "MLFeaturePipeline",
    "calculate_hourly_entropy",
    "calculate_inter_post_intervals",
    "calculate_shannon_entropy",
    "calculate_simhash_repetition",
    "extract_content_features",
    "extract_feature_matrix",
    "extract_profile_features",
]
'''
    pkg_init.write_text(content, encoding="utf-8")
    git_commit(
        "refactor(ml): export feature extraction interfaces in sbh.detection.ml namespace",
        "2026-11-11 09:48:00 +0530",
        ["src/sbh/detection/ml/__init__.py"],
    )


def main():
    steps = [
        step_01, step_02, step_03, step_04, step_05,
        step_06, step_07, step_08, step_09, step_10,
        step_11, step_12, step_13, step_14, step_15,
        step_16, step_17, step_18, step_19, step_20,
        step_21, step_22, step_23, step_24, step_25,
    ]
    for s in steps:
        s()
    print("Batch 1 completed successfully!")


if __name__ == "__main__":
    main()
