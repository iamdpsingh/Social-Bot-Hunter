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
