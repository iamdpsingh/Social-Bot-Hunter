"""Platform accounts and their observation history."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime

from sbh.schemas.records import AccountObservationRecord
from sbh.shared.ids import new_id
from sbh.shared.timeutil import from_db, iso_utc, utcnow
from sbh.storage.database import Database

_CHUNK = 400


@dataclass(frozen=True)
class AccountSeen:
    platform_account_id: str
    seen_at: datetime
    username: str | None = None
    display_name: str | None = None


@dataclass(frozen=True)
class ObservationRow:
    id: str
    platform_account_id: str  # public (platform) id
    observed_at: datetime
    username: str | None
    display_name: str | None
    follower_count: int | None
    following_count: int | None
    post_count: int | None
    has_bio: bool | None
    bio_length: int | None
    has_profile_image: bool | None
    has_display_name: bool | None
    account_created_at: datetime | None
    is_verified: bool | None
    is_private: bool | None


def _b(v: object) -> bool | None:
    return None if v is None else bool(v)


class AccountRepository:
    def __init__(self, db: Database, clock: Callable[[], datetime] = utcnow) -> None:
        self.db = db
        self.clock = clock

    def ensure_accounts(self, scan_id: str, platform: str, provenance: str,
                        items: Iterable[AccountSeen]) -> None:
        """Upsert accounts. first/last observed widen monotonically; the username only changes
        when the incoming observation is at least as recent as the stored one."""
        self.db.executemany(
            "INSERT INTO platform_accounts (id, platform, platform_account_id, username, display_name, "
            "first_observed_at, last_observed_at, first_seen_scan_id, metadata, provenance) "
            "VALUES (:id, :platform, :pid, :username, :display_name, :seen, :seen, :scan, '{}', :prov) "
            "ON CONFLICT (platform, platform_account_id) DO UPDATE SET "
            "first_observed_at = CASE WHEN excluded.first_observed_at < platform_accounts.first_observed_at "
            "  THEN excluded.first_observed_at ELSE platform_accounts.first_observed_at END, "
            "last_observed_at = CASE WHEN excluded.last_observed_at > platform_accounts.last_observed_at "
            "  THEN excluded.last_observed_at ELSE platform_accounts.last_observed_at END, "
            "username = CASE WHEN excluded.username IS NOT NULL "
            "  AND excluded.last_observed_at >= platform_accounts.last_observed_at "
            "  THEN excluded.username ELSE platform_accounts.username END, "
            "display_name = CASE WHEN excluded.display_name IS NOT NULL "
            "  AND excluded.last_observed_at >= platform_accounts.last_observed_at "
            "  THEN excluded.display_name ELSE platform_accounts.display_name END",
            [{"id": new_id(), "platform": platform, "pid": i.platform_account_id,
              "username": i.username, "display_name": i.display_name, "seen": iso_utc(i.seen_at),
              "scan": scan_id, "prov": provenance} for i in items],
        )

    def resolve_ids(self, platform: str, public_ids: Sequence[str]) -> dict[str, str]:
        """Map platform account IDs to internal IDs."""
        out: dict[str, str] = {}
        unique = sorted(set(public_ids))
        for i in range(0, len(unique), _CHUNK):
            chunk = unique[i : i + _CHUNK]
            params = {f"p{j}": v for j, v in enumerate(chunk)}
            params["platform"] = platform
            rows = self.db.query_all(
                "SELECT id, platform_account_id AS pid FROM platform_accounts WHERE platform = :platform "
                f"AND platform_account_id IN ({', '.join(f':p{j}' for j in range(len(chunk)))})",
                params,
            )
            out.update({r["pid"]: r["id"] for r in rows})
        return out

    def insert_observations(self, scan_id: str, collected_at: datetime, provenance: str,
                            records: Sequence[AccountObservationRecord], id_map: dict[str, str]) -> None:
        self.db.executemany(
            "INSERT INTO account_observations (id, platform_account_id, scan_id, observed_at, collected_at, "
            "username, display_name, follower_count, following_count, post_count, has_bio, bio_length, "
            "has_profile_image, has_display_name, account_created_at, is_verified, is_private, "
            "source_payload_sha256, provenance) VALUES (:id, :acc, :scan, :obs, :col, :username, :display, "
            ":followers, :following, :posts, :has_bio, :bio_len, :has_img, :has_disp, :created, :verified, "
            ":private, :sha, :prov) ON CONFLICT (platform_account_id, scan_id, observed_at) DO NOTHING",
            [{"id": new_id(), "acc": id_map[r.platform_account_id], "scan": scan_id,
              "obs": iso_utc(r.observed_at), "col": iso_utc(collected_at), "username": r.username,
              "display": r.display_name, "followers": r.follower_count, "following": r.following_count,
              "posts": r.post_count, "has_bio": r.has_bio, "bio_len": r.bio_length,
              "has_img": r.has_profile_image, "has_disp": r.has_display_name,
              "created": iso_utc(r.account_created_at) if r.account_created_at else None,
              "verified": r.is_verified, "private": r.is_private, "sha": r.payload_sha256,
              "prov": provenance} for r in records],
        )

    def scan_account_ids(self, scan_id: str) -> dict[str, str]:
        """public id -> internal id, for every account the scan observed, linked or authored."""
        rows = self.db.query_all(
            "SELECT a.id, a.platform_account_id AS pid FROM platform_accounts a WHERE a.id IN ("
            "SELECT platform_account_id FROM account_observations WHERE scan_id = :s "
            "UNION SELECT source_account_id FROM relationship_edges WHERE scan_id = :s "
            "UNION SELECT target_account_id FROM relationship_edges WHERE scan_id = :s "
            "UNION SELECT author_account_id FROM content_observations WHERE scan_id = :s)",
            {"s": scan_id},
        )
        return {r["pid"]: r["id"] for r in rows}

    def load_observations(self, scan_id: str, as_of: datetime) -> dict[str, list[ObservationRow]]:
        """Observation history (this scan and earlier ones) for every account the scan observed,
        oldest first. Later scans are excluded so re-analysis of an old scan is reproducible."""
        rows = self.db.query_all(
            "SELECT o.*, a.platform_account_id AS pid FROM account_observations o "
            "JOIN platform_accounts a ON a.id = o.platform_account_id "
            "WHERE o.platform_account_id IN "
            "  (SELECT platform_account_id FROM account_observations WHERE scan_id = :s) "
            "AND o.collected_at <= :asof ORDER BY a.platform_account_id, o.observed_at",
            {"s": scan_id, "asof": iso_utc(as_of)},
        )
        out: dict[str, list[ObservationRow]] = {}
        for r in rows:
            out.setdefault(r["pid"], []).append(ObservationRow(
                id=r["id"], platform_account_id=r["pid"], observed_at=from_db(r["observed_at"]),  # type: ignore[arg-type]
                username=r["username"], display_name=r["display_name"],
                follower_count=r["follower_count"], following_count=r["following_count"],
                post_count=r["post_count"], has_bio=_b(r["has_bio"]), bio_length=r["bio_length"],
                has_profile_image=_b(r["has_profile_image"]), has_display_name=_b(r["has_display_name"]),
                account_created_at=from_db(r["account_created_at"]), is_verified=_b(r["is_verified"]),
                is_private=_b(r["is_private"]),
            ))
        return out
