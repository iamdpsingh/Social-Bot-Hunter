"""Typed, validated configuration loaded from YAML.

Configuration is the only place thresholds and weights live. The loader rejects unknown
or missing keys so that a typo cannot silently fall back to a default.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any

import yaml

from sbh.shared import jsonutil
from sbh.shared.errors import ConfigError


@dataclass(frozen=True)
class RuleSpec:
    feature: str
    weight: float
    zero_at: float
    full_at: float
    description: str


@dataclass(frozen=True)
class BandSpec:
    lower: float
    label: str


@dataclass(frozen=True)
class ScoringConfig:
    rules: tuple[RuleSpec, ...]
    bands: tuple[BandSpec, ...]
    min_features: int
    min_weight_coverage: float


@dataclass(frozen=True)
class FeatureConfig:
    min_profile_fields: int
    min_account_age_days: float
    min_posts_for_interval: int
    min_posts_for_duplicates: int
    simhash_max_distance: int
    growth_min_gap_hours: float
    growth_follower_floor: int
    min_out_degree: int
    min_checkable_follows: int


@dataclass(frozen=True)
class GraphLimits:
    max_nodes: int
    max_edges: int
    max_pairs: int
    max_seconds: float


@dataclass(frozen=True)
class ClusterConfig:
    min_out_degree: int
    min_shared_targets: int
    jaccard_threshold: float
    min_cluster_size: int
    max_cluster_size: int
    shared_target_member_share: float
    popular_target_percentile: float
    content_duplication_threshold: float
    min_member_posts_for_content: int
    sync_window_seconds: float
    sync_min_posts_per_member: int
    sync_min_observed_pairs: int
    sync_lift_threshold: float
    high_reciprocity_threshold: float
    elevated_member_score: float
    elevated_member_share: float
    min_observation_fraction: float
    min_complete_list_fraction: float


@dataclass(frozen=True)
class GraphConfig:
    limits: GraphLimits
    max_posting_list: int
    feature_min_shared_targets: int
    louvain_seed: int
    cluster: ClusterConfig


@dataclass(frozen=True)
class ImportConfig:
    batch_size: int
    max_invalid_fraction: float
    future_skew_seconds: int
    max_records_per_file: int
    max_file_bytes: int
    max_identifier_length: int
    max_username_length: int
    max_display_name_length: int
    stale_observation_days: int
    missing_field_warn_fraction: float
    row_count_change_warn_ratio: float


@dataclass(frozen=True)
class Config:
    version: str
    scoring: ScoringConfig
    features: FeatureConfig
    graph: GraphConfig
    imports: ImportConfig
    raw: dict[str, Any]

    @property
    def sha256(self) -> str:
        return jsonutil.sha256_hex(jsonutil.dumps(self.raw))


def _section(data: dict[str, Any], key: str, path: str) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise ConfigError(f"{path}{key}: expected a mapping")
    return value


def _build(cls: type, data: dict[str, Any], path: str, skip: tuple[str, ...] = ()) -> Any:
    """Instantiate a flat dataclass from a mapping, coercing by the declared field type."""
    fields = {f: t for f, t in cls.__annotations__.items() if f not in skip}
    extra = set(data) - set(fields) - set(skip)
    if extra:
        raise ConfigError(f"{path}: unknown keys {sorted(extra)}")
    kwargs: dict[str, Any] = {}
    for name, annotation in fields.items():
        if name not in data:
            raise ConfigError(f"{path}{name}: missing")
        raw = data[name]
        ann = str(annotation)
        try:
            if "int" in ann and "float" not in ann:
                if isinstance(raw, bool) or int(raw) != raw:
                    raise ValueError("not an integer")
                kwargs[name] = int(raw)
            elif "float" in ann:
                if isinstance(raw, bool):
                    raise ValueError("not a number")
                kwargs[name] = float(raw)
            else:
                kwargs[name] = raw
        except (TypeError, ValueError) as exc:
            raise ConfigError(f"{path}{name}: {exc}") from exc
    return cls(**kwargs)


def _parse(raw: dict[str, Any]) -> Config:
    version = raw.get("version")
    if not isinstance(version, str) or not version:
        raise ConfigError("version: required non-empty string")

    sc = _section(raw, "scoring", "")
    rules: list[RuleSpec] = []
    for i, r in enumerate(sc.get("rules") or []):
        rules.append(_build(RuleSpec, r, f"scoring.rules[{i}]."))
    bands: list[BandSpec] = []
    for i, b in enumerate(sc.get("bands") or []):
        bands.append(_build(BandSpec, b, f"scoring.bands[{i}]."))
    for key in ("min_features", "min_weight_coverage"):
        if key not in sc:
            raise ConfigError(f"scoring.{key}: missing")
    try:
        scoring = ScoringConfig(
            rules=tuple(rules),
            bands=tuple(bands),
            min_features=int(sc["min_features"]),
            min_weight_coverage=float(sc["min_weight_coverage"]),
        )
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"scoring: {exc}") from exc

    g = _section(raw, "graph", "")
    gl = _build(GraphLimits, _section(g, "limits", "graph."), "graph.limits.")
    cluster = _build(ClusterConfig, _section(g, "cluster", "graph."), "graph.cluster.")
    graph = GraphConfig(
        limits=gl,
        cluster=cluster,
        **{
            "max_posting_list": int(g["max_posting_list"]),
            "feature_min_shared_targets": int(g["feature_min_shared_targets"]),
            "louvain_seed": int(g["louvain_seed"]),
        },
    )

    cfg = Config(
        version=version,
        scoring=scoring,
        features=_build(FeatureConfig, _section(raw, "features", ""), "features."),
        graph=graph,
        imports=_build(ImportConfig, _section(raw, "imports", ""), "imports."),
        raw=raw,
    )
    _validate(cfg)
    return cfg


def _validate(cfg: Config) -> None:
    s = cfg.scoring
    if not s.rules:
        raise ConfigError("scoring.rules: at least one rule required")
    names = [r.feature for r in s.rules]
    if len(set(names)) != len(names):
        raise ConfigError("scoring.rules: duplicate feature names")
    for r in s.rules:
        if r.weight <= 0:
            raise ConfigError(f"scoring.rules[{r.feature}].weight must be > 0")
        if r.zero_at == r.full_at:
            raise ConfigError(f"scoring.rules[{r.feature}]: zero_at and full_at must differ")
    if not 0 < s.min_weight_coverage <= 1:
        raise ConfigError("scoring.min_weight_coverage must be in (0, 1]")
    if s.min_features < 1 or s.min_features > len(s.rules):
        raise ConfigError("scoring.min_features must be between 1 and the number of rules")
    lowers = [b.lower for b in s.bands]
    if not lowers or lowers[0] != 0 or lowers != sorted(lowers) or len(set(lowers)) != len(lowers):
        raise ConfigError("scoring.bands: lower bounds must start at 0 and strictly increase")
    c = cfg.graph.cluster
    if not 0 < c.jaccard_threshold <= 1:
        raise ConfigError("graph.cluster.jaccard_threshold must be in (0, 1]")
    if c.min_cluster_size < 2 or c.max_cluster_size < c.min_cluster_size:
        raise ConfigError("graph.cluster size bounds are inconsistent")
    if not 0 <= cfg.imports.max_invalid_fraction <= 1:
        raise ConfigError("imports.max_invalid_fraction must be in [0, 1]")
    if cfg.imports.batch_size < 1:
        raise ConfigError("imports.batch_size must be >= 1")
    if cfg.graph.limits.max_nodes < 1 or cfg.graph.limits.max_edges < 1:
        raise ConfigError("graph.limits must be positive")


def load_config(path: str | os.PathLike[str] | None = None) -> Config:
    """Load configuration from ``path``, ``$SBH_CONFIG_PATH``, or the packaged default."""
    chosen = path or os.environ.get("SBH_CONFIG_PATH")
    try:
        if chosen:
            text = Path(chosen).read_text(encoding="utf-8")
        else:
            text = resources.files("sbh.resources").joinpath("detection.v1.yaml").read_text("utf-8")
    except OSError as exc:
        raise ConfigError(f"cannot read configuration: {exc}") from exc
    try:
        raw = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ConfigError(f"invalid YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise ConfigError("configuration root must be a mapping")
    return _parse(raw)
