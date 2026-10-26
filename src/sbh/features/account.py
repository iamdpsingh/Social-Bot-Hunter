"""Account-level features. Each function uses only data the source actually supplied.

Nothing here infers an account creation date, treats verification as proof of anything, or
turns a missing value into zero. When inputs are missing the feature is *unavailable* with a
stated reason.
"""

from __future__ import annotations

import statistics
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime

from sbh.config import FeatureConfig
from sbh.features.definitions import FeatureResult
from sbh.ingestion.fingerprint import duplicate_components
from sbh.shared.models import Post
from sbh.storage.accounts import ObservationRow

_MAX_POSTS_FOR_DUPLICATES = 2000
_DAY = 86400.0


@dataclass(frozen=True)
class AccountContext:
    public_id: str
    observations: Sequence[ObservationRow]  # oldest first; may be empty
    posts: Sequence[Post]
    content_collected: bool  # did this scan collect any content at all?
    out_degree: int | None = None
    in_degree: int | None = None
    checkable_follows: int | None = None
    mutual_count: int | None = None
    max_following_jaccard: float | None = None
    list_completeness: dict[str, str] = field(default_factory=dict)  # kind -> completeness


def _latest(ctx: AccountContext) -> ObservationRow | None:
    return ctx.observations[-1] if ctx.observations else None


def following_follower_ratio(ctx: AccountContext) -> FeatureResult:
    name = "following_follower_ratio"
    obs = _latest(ctx)
    if obs is None:
        return FeatureResult.unavailable(name, "no profile observation")
    if obs.follower_count is None or obs.following_count is None:
        return FeatureResult.unavailable(name, "follower_count or following_count not observed")
    ratio = (obs.following_count + 1) / (obs.follower_count + 1)
    return FeatureResult.ok(name, ratio, followers=obs.follower_count, following=obs.following_count,
                            observation_id=obs.id)


def profile_completeness(ctx: AccountContext, cfg: FeatureConfig) -> FeatureResult:
    name = "profile_completeness"
    obs = _latest(ctx)
    if obs is None:
        return FeatureResult.unavailable(name, "no profile observation")
    fields = {"bio": obs.has_bio, "profile_image": obs.has_profile_image, "display_name": obs.has_display_name}
    known = {k: v for k, v in fields.items() if v is not None}
    if len(known) < cfg.min_profile_fields:
        return FeatureResult.unavailable(
            name, f"only {len(known)} profile field(s) observed; need {cfg.min_profile_fields}")
    present = sum(1 for v in known.values() if v)
    return FeatureResult.ok(name, present / len(known), fields_known=sorted(known),
                            fields_present=sorted(k for k, v in known.items() if v), observation_id=obs.id)


def username_digit_ratio(ctx: AccountContext) -> FeatureResult:
    name = "username_digit_ratio"
    for obs in reversed(ctx.observations):
        if obs.username:
            digits = sum(1 for ch in obs.username if ch.isdecimal())
            return FeatureResult.ok(name, digits / len(obs.username), username_length=len(obs.username),
                                    observation_id=obs.id)
    return FeatureResult.unavailable(name, "username not observed")


def post_rate_per_day(ctx: AccountContext, cfg: FeatureConfig) -> FeatureResult:
    name = "post_rate_per_day"
    obs = _latest(ctx)
    if obs is None:
        return FeatureResult.unavailable(name, "no profile observation")
    if obs.post_count is None:
        return FeatureResult.unavailable(name, "post_count not observed")
    if obs.account_created_at is None:
        return FeatureResult.unavailable(name, "account creation time not supplied by the source")
    age_days = (obs.observed_at - obs.account_created_at).total_seconds() / _DAY
    if age_days < cfg.min_account_age_days:
        return FeatureResult.unavailable(
            name, f"account only {age_days:.1f} days old at observation; rate would be unstable")
    return FeatureResult.ok(name, obs.post_count / age_days, post_count=obs.post_count,
                            account_age_days=round(age_days, 2), observation_id=obs.id)


def post_interval_cv(ctx: AccountContext, cfg: FeatureConfig) -> FeatureResult:
    name = "post_interval_cv"
    if not ctx.content_collected:
        return FeatureResult.unavailable(name, "no content observations in this scan")
    ts = sorted(p.ts for p in ctx.posts)
    if len(ts) < cfg.min_posts_for_interval:
        return FeatureResult.unavailable(
            name, f"{len(ts)} posts observed; need {cfg.min_posts_for_interval}", posts=len(ts))
    gaps = [b - a for a, b in zip(ts, ts[1:], strict=False)]
    mean = statistics.fmean(gaps)
    if mean == 0:
        return FeatureResult.ok(name, 0.0, posts=len(ts), all_posts_same_timestamp=True)
    return FeatureResult.ok(name, statistics.pstdev(gaps) / mean, posts=len(ts),
                            mean_gap_seconds=round(mean, 1))


def duplicate_content_ratio(ctx: AccountContext, cfg: FeatureConfig) -> FeatureResult:
    name = "duplicate_content_ratio"
    if not ctx.content_collected:
        return FeatureResult.unavailable(name, "no content observations in this scan")
    fingerprinted = [p for p in ctx.posts if p.content_hash is not None or p.simhash is not None]
    if len(fingerprinted) < cfg.min_posts_for_duplicates:
        return FeatureResult.unavailable(
            name, f"{len(fingerprinted)} fingerprinted posts; need {cfg.min_posts_for_duplicates}")
    truncated = len(fingerprinted) > _MAX_POSTS_FOR_DUPLICATES
    sample = sorted(fingerprinted, key=lambda p: p.ts)[-_MAX_POSTS_FOR_DUPLICATES:]
    labels = duplicate_components([(p.content_hash, p.simhash) for p in sample], cfg.simhash_max_distance)
    sizes: dict[int, int] = {}
    for lab in labels:
        sizes[lab] = sizes.get(lab, 0) + 1
    dup = sum(1 for lab in labels if sizes[lab] >= 2)
    return FeatureResult.ok(name, dup / len(sample), posts_considered=len(sample), duplicated_posts=dup,
                            truncated_to_most_recent=truncated)


def follower_growth_spike(ctx: AccountContext, cfg: FeatureConfig) -> FeatureResult:
    name = "follower_growth_spike"
    pts = [(o.observed_at, o.follower_count) for o in ctx.observations if o.follower_count is not None]
    best: float | None = None
    detail: dict[str, object] = {}
    for (t1, f1), (t2, f2) in zip(pts, pts[1:], strict=False):
        assert f1 is not None and f2 is not None
        if (t2 - t1).total_seconds() < cfg.growth_min_gap_hours * 3600:
            continue
        rel = max(0.0, (f2 - f1) / max(f1, cfg.growth_follower_floor))
        if best is None or rel > best:
            best = rel
            detail = {"from": t1.isoformat(), "to": t2.isoformat(), "followers_before": f1,
                      "followers_after": f2}
    if best is None:
        return FeatureResult.unavailable(
            name, f"fewer than two follower-count observations at least {cfg.growth_min_gap_hours}h apart")
    return FeatureResult.ok(name, best, **detail)


def max_following_jaccard(ctx: AccountContext, cfg: FeatureConfig) -> FeatureResult:
    name = "max_following_jaccard"
    if ctx.out_degree is None:
        return FeatureResult.unavailable(name, "no relationship data in this scan")
    if ctx.out_degree < cfg.min_out_degree:
        return FeatureResult.unavailable(
            name, f"{ctx.out_degree} observed follows; need {cfg.min_out_degree}", out_degree=ctx.out_degree)
    return FeatureResult.ok(name, ctx.max_following_jaccard or 0.0, out_degree=ctx.out_degree,
                            following_list=ctx.list_completeness.get("following", "unknown"))


def reciprocity_ratio(ctx: AccountContext, cfg: FeatureConfig) -> FeatureResult:
    name = "reciprocity_ratio"
    if ctx.checkable_follows is None or ctx.mutual_count is None:
        return FeatureResult.unavailable(name, "no relationship data in this scan")
    if ctx.checkable_follows < cfg.min_checkable_follows:
        return FeatureResult.unavailable(
            name, f"only {ctx.checkable_follows} followed account(s) have a complete following list to "
                  f"check follow-back against; need {cfg.min_checkable_follows}",
            checkable_follows=ctx.checkable_follows)
    return FeatureResult.ok(name, ctx.mutual_count / ctx.checkable_follows,
                            checkable_follows=ctx.checkable_follows, mutual=ctx.mutual_count,
                            out_degree=ctx.out_degree)


def observation_age_days(ctx: AccountContext, reference_time: datetime) -> FeatureResult:
    name = "observation_age_days"
    obs = _latest(ctx)
    if obs is None:
        return FeatureResult.unavailable(name, "no profile observation")
    return FeatureResult.ok(name, max(0.0, (reference_time - obs.observed_at).total_seconds() / _DAY),
                            observed_at=obs.observed_at.isoformat())


_AVAILABILITY_FIELDS = ("username", "follower_count", "following_count", "post_count", "has_bio",
                        "has_profile_image", "has_display_name", "account_created_at")


def field_availability(ctx: AccountContext) -> FeatureResult:
    name = "field_availability"
    obs = _latest(ctx)
    if obs is None:
        return FeatureResult.unavailable(name, "no profile observation")
    present = [f for f in _AVAILABILITY_FIELDS if getattr(obs, f) is not None]
    return FeatureResult.ok(name, len(present) / len(_AVAILABILITY_FIELDS),
                            missing=[f for f in _AVAILABILITY_FIELDS if f not in present])


def observation_count(ctx: AccountContext) -> FeatureResult:
    if not ctx.observations:
        return FeatureResult.unavailable("observation_count", "no profile observation")
    return FeatureResult.ok("observation_count", len(ctx.observations))


def relationship_coverage(ctx: AccountContext) -> FeatureResult:
    name = "relationship_coverage"
    if not ctx.list_completeness:
        return FeatureResult.unavailable(name, "no relationship list recorded for this account")
    complete = sum(1 for c in ctx.list_completeness.values() if c == "complete")
    return FeatureResult.ok(name, complete / 2, lists=dict(sorted(ctx.list_completeness.items())))


def posts_observed(ctx: AccountContext) -> FeatureResult:
    if not ctx.content_collected:
        return FeatureResult.unavailable("posts_observed", "no content observations in this scan")
    return FeatureResult.ok("posts_observed", len(ctx.posts))


def compute_account_features(ctx: AccountContext, cfg: FeatureConfig,
                             reference_time: datetime) -> list[FeatureResult]:
    return [
        following_follower_ratio(ctx),
        profile_completeness(ctx, cfg),
        username_digit_ratio(ctx),
        post_rate_per_day(ctx, cfg),
        post_interval_cv(ctx, cfg),
        duplicate_content_ratio(ctx, cfg),
        follower_growth_spike(ctx, cfg),
        max_following_jaccard(ctx, cfg),
        reciprocity_ratio(ctx, cfg),
        observation_age_days(ctx, reference_time),
        field_availability(ctx),
        observation_count(ctx),
        relationship_coverage(ctx),
        posts_observed(ctx),
    ]
