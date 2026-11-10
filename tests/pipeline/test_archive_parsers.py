"""Unit tests for archive format parsers and Ingestor."""

from __future__ import annotations

from pathlib import Path
from sbh.pipeline.archive_ingest import DatasetFormat, ExtractedArchive
from sbh.pipeline.archive_parsers import (
    ArchiveBatchIngestor,
    CSVManifestParser,
    NDJSONArchiveParser,
    TwitterArchiveParser,
)
from sbh.schemas.records import ContentRecord

SAMPLE_TWEET_JS = """window.YTD.tweet.part0 = [
  {
    "tweet": {
      "id": "1800000001",
      "full_text": "Sample tweet for archive parser verification #testing",
      "created_at": "Wed Nov 04 10:15:30 +0000 2026",
      "favorite_count": 42,
      "retweet_count": 12,
      "user_id": "99999"
    }
  }
];"""
