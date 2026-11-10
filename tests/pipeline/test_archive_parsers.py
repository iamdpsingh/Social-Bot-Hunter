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

def test_twitter_archive_parser_stream(tmp_path: Path) -> None:
    tweet_file = tmp_path / "tweet.js"
    tweet_file.write_text(SAMPLE_TWEET_JS)
    parser = TwitterArchiveParser()
    records = list(parser.parse_content(tweet_file))
    assert len(records) == 1
    rec = records[0]
    assert isinstance(rec, ContentRecord)
    assert rec.platform == "x"
    assert rec.platform_content_id == "1800000001"

def test_twitter_archive_parser_metrics(tmp_path: Path) -> None:
    tweet_file = tmp_path / "tweet.js"
    tweet_file.write_text(SAMPLE_TWEET_JS)
    parser = TwitterArchiveParser()
    rec = list(parser.parse_content(tweet_file))[0]
    assert isinstance(rec, ContentRecord)
    assert rec.like_count == 42
    assert rec.share_count == 12
    assert rec.simhash is not None and rec.simhash > 0

def test_twitter_archive_account_parsing(tmp_path: Path) -> None:
    acc_file = tmp_path / "account.js"
    acc_file.write_text('window.YTD.account.part0 = [{"account": {"accountId": "99999", "username": "alice", "bio": "cyber researcher"}}];')
    parser = TwitterArchiveParser()
    accounts = list(parser.parse_accounts(acc_file))
    assert len(accounts) == 1
    assert accounts[0].username == "alice"
    assert accounts[0].has_bio is True
