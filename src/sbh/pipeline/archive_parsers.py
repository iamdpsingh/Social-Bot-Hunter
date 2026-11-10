"""Archive and dataset format parsers converting files to domain records."""

from __future__ import annotations

import csv
import json
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator

from sbh.detection.simhash import compute_simhash
from sbh.pipeline.archive_ingest import DatasetFormat, ExtractedArchive
from sbh.schemas.records import AccountObservationRecord, ContentRecord, QuarantinedRecord

class BaseArchiveParser(ABC):
    """Abstract base class for dataset archive parsers."""

    @abstractmethod
    def parse_content(self, target_path: Path) -> Iterator[ContentRecord | QuarantinedRecord]:
        """Stream content records or quarantined records from target path."""

    @abstractmethod
    def parse_accounts(self, target_path: Path) -> Iterator[AccountObservationRecord | QuarantinedRecord]:
        """Stream account observation records from target path."""


@dataclass
class IngestionBatchSummary:
    """Aggregated outcome of an archive parsing and ingestion operation."""
    archive_format: DatasetFormat
    accounts: list[AccountObservationRecord] = field(default_factory=list)
    content: list[ContentRecord] = field(default_factory=list)
    quarantined: list[QuarantinedRecord] = field(default_factory=list)
    elapsed_ms: float = 0.0
    total_records: int = 0


class TwitterArchiveParser(BaseArchiveParser):
    """Parses official Twitter (X) data download archives."""

    @staticmethod
    def _strip_js_prefix(content: str) -> str:
        """Strip Javascript assignment variable prefix (e.g. window.YTD.tweet.part0 = [...])."""
        match = re.search(r"^[a-zA-Z0-9_$.]+\s*=\s*", content.strip())
        if match:
            return content.strip()[match.end():]
        return content.strip()

    @staticmethod
    def _tweet_to_record(item: dict[str, Any], source_ref: str) -> ContentRecord | QuarantinedRecord:
        """Map tweet payload to ContentRecord or QuarantinedRecord if invalid."""
        raw_tweet = item.get("tweet", item)
        tweet_id = str(raw_tweet.get("id") or raw_tweet.get("id_str") or "")
        if not tweet_id:
            return QuarantinedRecord(
                entity="content",
                source_ref=source_ref,
                kind="invalid",
                reasons=("missing_content_id",),
                raw=raw_tweet,
            )
        text = raw_tweet.get("full_text") or raw_tweet.get("text") or ""
        dt_str = raw_tweet.get("created_at") or ""
        try:
            # Format: "Wed Oct 10 20:19:24 +0000 2018"
            published_at = datetime.strptime(dt_str, "%a %b %d %H:%M:%S %z %Y") if dt_str else datetime.now(UTC)
        except ValueError:
            published_at = datetime.now(UTC)

        simhash = compute_simhash(text) if text else 0
        return ContentRecord(
            platform="x",
            platform_content_id=tweet_id,
            author_account_id=str(raw_tweet.get("user_id") or "unknown"),
            published_at=published_at,
            simhash=simhash,
            text_length=len(text),
            like_count=int(raw_tweet.get("favorite_count", 0)),
            share_count=int(raw_tweet.get("retweet_count", 0)),
            reply_count=None,
            source_ref=source_ref,
        )

    def parse_content(self, target_path: Path) -> Iterator[ContentRecord | QuarantinedRecord]:
        """Stream tweets from data/tweet.js file."""
        if not target_path.exists():
            return
        raw_text = target_path.read_text(encoding="utf-8", errors="replace")
        clean_json = self._strip_js_prefix(raw_text)
        try:
            data = json.loads(clean_json)
        except json.JSONDecodeError as exc:
            yield QuarantinedRecord(
                entity="content",
                source_ref=str(target_path),
                kind="invalid",
                reasons=(f"json_decode_error: {exc}",),
            )
            return
        if isinstance(data, list):
            for item in data:
                yield self._tweet_to_record(item, str(target_path))

    def parse_accounts(self, target_path: Path) -> Iterator[AccountObservationRecord | QuarantinedRecord]:
        """Stream account observation from account.js."""
        if not target_path.exists():
            return
        raw_text = target_path.read_text(encoding="utf-8", errors="replace")
        clean_json = self._strip_js_prefix(raw_text)
        try:
            data = json.loads(clean_json)
        except json.JSONDecodeError:
            return
        items = data if isinstance(data, list) else [data]
        for item in items:
            acc = item.get("account", item)
            account_id = str(acc.get("accountId") or acc.get("id") or "")
            if not account_id:
                continue
            yield AccountObservationRecord(
                platform="x",
                platform_account_id=account_id,
                observed_at=datetime.now(UTC),
                username=acc.get("username") or acc.get("screen_name"),
                display_name=acc.get("accountDisplayName"),
                has_bio=bool(acc.get("bio")),
                source_ref=str(target_path),
            )


class NDJSONArchiveParser(BaseArchiveParser):
    """Memory-efficient streaming parser for NDJSON / JSONL dataset feeds."""

    @staticmethod
    def _read_lines(target_path: Path) -> Iterator[tuple[int, dict[str, Any] | str]]:
        """Yield line number and parsed JSON object or raw line string on decode failure."""
        with open(target_path, "r", encoding="utf-8", errors="replace") as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    yield line_no, json.loads(line)
                except json.JSONDecodeError:
                    yield line_no, line

    @staticmethod
    def _is_content(doc: dict[str, Any]) -> bool:
        """Heuristically identify whether document represents post/content vs user profile."""
        content_keys = {"text", "content", "full_text", "caption", "body", "post_id", "tweet_id"}
        return bool(set(doc.keys()) & content_keys)

    def parse_content(self, target_path: Path) -> Iterator[ContentRecord | QuarantinedRecord]:
        """Stream content records from NDJSON file."""
        if not target_path.exists():
            return
        for line_no, entry in self._read_lines(target_path):
            if isinstance(entry, str):
                yield QuarantinedRecord(
                    entity="content",
                    source_ref=f"{target_path}:{line_no}",
                    kind="invalid",
                    reasons=("json_decode_error",),
                )
                continue
            if not self._is_content(entry):
                continue
            cid = str(entry.get("id") or entry.get("content_id") or entry.get("post_id") or f"line_{line_no}")
            author = str(entry.get("author_id") or entry.get("user_id") or entry.get("author") or "unknown")
            text = str(entry.get("text") or entry.get("content") or entry.get("caption") or "")
            simhash = compute_simhash(text) if text else 0
            yield ContentRecord(
                platform=str(entry.get("platform") or "unknown"),
                platform_content_id=cid,
                author_account_id=author,
                published_at=datetime.now(UTC),
                simhash=simhash,
                text_length=len(text),
                like_count=entry.get("likes") or entry.get("like_count"),
                reply_count=entry.get("replies") or entry.get("reply_count"),
                share_count=entry.get("shares") or entry.get("share_count"),
                source_ref=f"{target_path}:{line_no}",
            )

    def parse_accounts(self, target_path: Path) -> Iterator[AccountObservationRecord | QuarantinedRecord]:
        """Stream account records from NDJSON file."""
        if not target_path.exists():
            return
        for line_no, entry in self._read_lines(target_path):
            if isinstance(entry, str) or self._is_content(entry):
                continue
            account_id = str(entry.get("id") or entry.get("account_id") or entry.get("user_id") or "")
            if not account_id:
                continue
            yield AccountObservationRecord(
                platform=str(entry.get("platform") or "unknown"),
                platform_account_id=account_id,
                observed_at=datetime.now(UTC),
                username=entry.get("username") or entry.get("handle"),
                display_name=entry.get("name") or entry.get("display_name"),
                follower_count=entry.get("follower_count") or entry.get("followers"),
                following_count=entry.get("following_count") or entry.get("following"),
                source_ref=f"{target_path}:{line_no}",
            )


class CSVManifestParser(BaseArchiveParser):
    """Robust CSV table transformer handling multiple column naming conventions."""

    @staticmethod
    def _normalize_row(row: dict[str, str]) -> dict[str, str]:
        """Strip whitespaces and lower-case keys for normalized lookup."""
        return {k.strip().lower(): v.strip() for k, v in row.items() if k}

    def parse_content(self, target_path: Path) -> Iterator[ContentRecord | QuarantinedRecord]:
        """Stream content records from CSV table."""
        if not target_path.exists():
            return
        with open(target_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for idx, raw_row in enumerate(reader, start=1):
                row = self._normalize_row(raw_row)
                cid = row.get("id") or row.get("content_id") or row.get("post_id") or str(idx)
                text = row.get("text") or row.get("content") or row.get("caption") or ""
                author = row.get("author") or row.get("user_id") or row.get("author_account_id") or "unknown"
                simhash = compute_simhash(text) if text else 0
                yield ContentRecord(
                    platform=row.get("platform", "csv_import"),
                    platform_content_id=cid,
                    author_account_id=author,
                    published_at=datetime.now(UTC),
                    simhash=simhash,
                    text_length=len(text),
                    like_count=int(row["likes"]) if "likes" in row and row["likes"].isdigit() else None,
                    reply_count=int(row["replies"]) if "replies" in row and row["replies"].isdigit() else None,
                    share_count=int(row["shares"]) if "shares" in row and row["shares"].isdigit() else None,
                    source_ref=f"{target_path}:{idx}",
                )

    def parse_accounts(self, target_path: Path) -> Iterator[AccountObservationRecord | QuarantinedRecord]:
        """Stream account records from CSV table."""
        if not target_path.exists():
            return
        with open(target_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for idx, raw_row in enumerate(reader, start=1):
                row = self._normalize_row(raw_row)
                aid = row.get("id") or row.get("account_id") or row.get("user_id") or str(idx)
                yield AccountObservationRecord(
                    platform=row.get("platform", "csv_import"),
                    platform_account_id=aid,
                    observed_at=datetime.now(UTC),
                    username=row.get("username") or row.get("handle"),
                    display_name=row.get("display_name") or row.get("name"),
                    follower_count=int(row["followers"]) if "followers" in row and row["followers"].isdigit() else None,
                    following_count=int(row["following"]) if "following" in row and row["following"].isdigit() else None,
                    source_ref=f"{target_path}:{idx}",
                )


class ArchiveBatchIngestor:
    """Coordinates dataset archive extraction, parser dispatch, and entity validation."""

    def __init__(self) -> None:
        self.parsers: dict[DatasetFormat, BaseArchiveParser] = {
            DatasetFormat.TWITTER_ARCHIVE: TwitterArchiveParser(),
            DatasetFormat.NDJSON: NDJSONArchiveParser(),
            DatasetFormat.CSV: CSVManifestParser(),
        }

    def ingest(self, extracted: ExtractedArchive) -> IngestionBatchSummary:
        """Execute batch transformation across extracted dataset artifacts."""
        start_time = time.perf_counter()
        parser = self.parsers.get(extracted.format)
        if not parser or not extracted.records_path:
            return IngestionBatchSummary(archive_format=extracted.format)
