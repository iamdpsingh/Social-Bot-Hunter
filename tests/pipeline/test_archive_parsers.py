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

def test_ndjson_parser_content(tmp_path: Path) -> None:
    ndjson_file = tmp_path / "stream.ndjson"
    ndjson_file.write_text('{"id": "p1", "text": "automated message 1", "author": "u1", "likes": 5}\n')
    parser = NDJSONArchiveParser()
    records = list(parser.parse_content(ndjson_file))
    assert len(records) == 1
    rec = records[0]
    assert isinstance(rec, ContentRecord)
    assert rec.platform_content_id == "p1"
    assert rec.like_count == 5

def test_ndjson_parser_accounts(tmp_path: Path) -> None:
    ndjson_file = tmp_path / "users.ndjson"
    ndjson_file.write_text('{"account_id": "u100", "username": "bot_target", "followers": 50}\n')
    parser = NDJSONArchiveParser()
    accounts = list(parser.parse_accounts(ndjson_file))
    assert len(accounts) == 1
    assert accounts[0].platform_account_id == "u100"
    assert accounts[0].follower_count == 50

def test_ndjson_invalid_line_quarantine(tmp_path: Path) -> None:
    ndjson_file = tmp_path / "corrupted.ndjson"
    ndjson_file.write_text('not a valid json object line\n{"id": "p2", "text": "valid"}\n')
    parser = NDJSONArchiveParser()
    records = list(parser.parse_content(ndjson_file))
    assert len(records) == 2
    assert records[0].__class__.__name__ == "QuarantinedRecord"
    assert isinstance(records[1], ContentRecord)

def test_csv_parser_content(tmp_path: Path) -> None:
    csv_file = tmp_path / "feed.csv"
    csv_file.write_text("post_id,author,content,likes\nc1,alice,hello world,15\n")
    parser = CSVManifestParser()
    records = list(parser.parse_content(csv_file))
    assert len(records) == 1
    rec = records[0]
    assert isinstance(rec, ContentRecord)
    assert rec.platform_content_id == "c1"
    assert rec.like_count == 15

def test_csv_parser_accounts(tmp_path: Path) -> None:
    csv_file = tmp_path / "profiles.csv"
    csv_file.write_text("account_id,handle,name,followers\n1234,bob,Bob Smith,500\n")
    parser = CSVManifestParser()
    accounts = list(parser.parse_accounts(csv_file))
    assert len(accounts) == 1
    assert accounts[0].platform_account_id == "1234"
    assert accounts[0].username == "bob"
    assert accounts[0].follower_count == 500

def test_csv_empty_rows(tmp_path: Path) -> None:
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("id,text\n")
    parser = CSVManifestParser()
    assert len(list(parser.parse_content(csv_file))) == 0

def test_batch_ingestor_twitter(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    tweet_file = data_dir / "tweet.js"
    tweet_file.write_text(SAMPLE_TWEET_JS)
    ext = ExtractedArchive(
        extracted_path=tmp_path,
        format=DatasetFormat.TWITTER_ARCHIVE,
        file_count=1,
        total_uncompressed_bytes=len(SAMPLE_TWEET_JS),
        records_path=tweet_file,
    )
    ingestor = ArchiveBatchIngestor()
    summary = ingestor.ingest(ext)
    assert summary.total_records == 1
    assert len(summary.content) == 1
    assert summary.content[0].platform_content_id == "1800000001"
