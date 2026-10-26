"""Content observations (fingerprints only; raw text is never stored)."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime

from sbh.schemas.records import ContentRecord
from sbh.shared.ids import new_id
from sbh.shared.timeutil import from_db, iso_utc, utcnow
from sbh.storage.database import Database


@dataclass(frozen=True)
class ContentRow:
    author: str  # public account id
    published_at: datetime
    content_hash: str | None
    simhash: int | None


class ContentRepository:
    def __init__(self, db: Database, clock: Callable[[], datetime] = utcnow) -> None:
        self.db = db
        self.clock = clock

    def insert_content(self, scan_id: str, collected_at: datetime, provenance: str,
                       records: Sequence[ContentRecord], id_map: dict[str, str]) -> None:
        self.db.executemany(
            "INSERT INTO content_observations (id, scan_id, platform, platform_content_id, author_account_id, "
            "published_at, collected_at, content_hash, simhash, text_length, like_count, reply_count, "
            "share_count, provenance) VALUES (:id, :scan, :platform, :cid, :author, :pub, :col, :hash, :sim, "
            ":tlen, :likes, :replies, :shares, :prov) "
            "ON CONFLICT (scan_id, platform, platform_content_id) DO NOTHING",
            [{"id": new_id(), "scan": scan_id, "platform": r.platform, "cid": r.platform_content_id,
              "author": id_map[r.author_account_id], "pub": iso_utc(r.published_at),
              "col": iso_utc(collected_at), "hash": r.content_hash,
              "sim": None if r.simhash is None else f"{r.simhash:016x}", "tlen": r.text_length,
              "likes": r.like_count, "replies": r.reply_count, "shares": r.share_count, "prov": provenance}
             for r in records],
        )

    def load_content(self, scan_id: str) -> list[ContentRow]:
        rows = self.db.query_all(
            "SELECT a.platform_account_id AS author, c.published_at, c.content_hash, c.simhash "
            "FROM content_observations c JOIN platform_accounts a ON a.id = c.author_account_id "
            "WHERE c.scan_id = :s ORDER BY author, c.published_at, c.platform_content_id", {"s": scan_id})
        return [ContentRow(r["author"], from_db(r["published_at"]),  # type: ignore[arg-type]
                           r["content_hash"], None if r["simhash"] is None else int(r["simhash"], 16))
                for r in rows]
