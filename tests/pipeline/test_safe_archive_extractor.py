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
