"""Unit tests for DatasetFormatDetector structure discovery."""

from __future__ import annotations

from pathlib import Path

from sbh.pipeline.archive_ingest import DatasetFormat, DatasetFormatDetector


def test_detect_twitter_archive(tmp_path: Path) -> None:
    dir_path = tmp_path / "twitter"
    data_dir = dir_path / "data"
    data_dir.mkdir(parents=True)
    (dir_path / "manifest.js").write_text("window.__THAR_CONFIG = {};")
    (data_dir / "tweet.js").write_text("window.YTD.tweet.part0 = [];")
    fmt, entry_file, platform = DatasetFormatDetector.detect(dir_path)
    assert fmt == DatasetFormat.TWITTER_ARCHIVE
    assert platform == "x"
    assert entry_file is not None and entry_file.name == "tweet.js"

def test_detect_ndjson_dataset(tmp_path: Path) -> None:
    dir_path = tmp_path / "ndjson"
    dir_path.mkdir()
    feed = dir_path / "feed.ndjson"
    feed.write_text('{"text": "msg 1"}\n{"text": "msg 2"}\n')
    fmt, entry_file, platform = DatasetFormatDetector.detect(dir_path)
    assert fmt == DatasetFormat.NDJSON
    assert entry_file == feed

def test_detect_csv_dataset(tmp_path: Path) -> None:
    dir_path = tmp_path / "csv"
    dir_path.mkdir()
    table = dir_path / "profiles.csv"
    table.write_text("id,username,followers\n1,alice,100\n")
    fmt, entry_file, platform = DatasetFormatDetector.detect(dir_path)
    assert fmt == DatasetFormat.CSV
    assert entry_file == table

def test_detect_generic_json(tmp_path: Path) -> None:
    dir_path = tmp_path / "json"
    dir_path.mkdir()
    blob = dir_path / "records.json"
    blob.write_text('{"items": []}')
    fmt, entry_file, platform = DatasetFormatDetector.detect(dir_path)
    assert fmt == DatasetFormat.GENERIC_JSON
    assert entry_file == blob

def test_detect_unknown(tmp_path: Path) -> None:
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    fmt, entry_file, platform = DatasetFormatDetector.detect(empty_dir)
    assert fmt == DatasetFormat.UNKNOWN
    assert entry_file is None
