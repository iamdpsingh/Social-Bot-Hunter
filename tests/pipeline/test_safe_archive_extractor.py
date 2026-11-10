"""Unit tests for SafeArchiveExtractor and safe unpacking."""

from __future__ import annotations

from pathlib import Path

from tests.pipeline.archive_test_utils import make_zip

from sbh.pipeline.archive_ingest import (
    SafeArchiveExtractor,
)


def test_valid_zip_extraction(tmp_path: Path) -> None:
    zip_path = tmp_path / "dataset.zip"
    make_zip(zip_path, {"data.json": '{"test": true}', "readme.txt": "hello"})
    dest = tmp_path / "extracted"
    extractor = SafeArchiveExtractor()
    count, total_bytes = extractor._extract_zip(zip_path, dest)
    assert count == 2
    assert total_bytes > 0
    assert (dest / "data.json").read_text() == '{"test": true}'

def test_valid_tar_gz_extraction(tmp_path: Path) -> None:
    tar_path = tmp_path / "dataset.tar.gz"
    make_tar(tar_path, {"records.csv": "id,name\n1,alice\n", "manifest.txt": "v1.0"})
    dest = tmp_path / "tar_out"
    extractor = SafeArchiveExtractor()
    count, total_bytes = extractor._extract_tar(tar_path, dest)
    assert count == 2
    assert (dest / "records.csv").exists()

def test_extract_and_detect_high_level(tmp_path: Path) -> None:
    zip_path = tmp_path / "feed.zip"
    make_zip(zip_path, {"stream.ndjson": '{"id": 1}\n{"id": 2}\n'})
    result = extract_and_detect_archive(zip_path)
    assert result.file_count == 1
    assert result.format == DatasetFormat.NDJSON
    assert result.records_path is not None
