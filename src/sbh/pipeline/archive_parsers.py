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
