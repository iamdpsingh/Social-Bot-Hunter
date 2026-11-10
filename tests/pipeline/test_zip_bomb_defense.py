"""Security tests for algorithmic zip-bomb defenses."""

from __future__ import annotations

from pathlib import Path

import pytest
from tests.pipeline.archive_test_utils import make_zip

from sbh.pipeline.archive_ingest import ArchiveSecurityError, SafeArchiveExtractor


def test_zip_bomb_compression_ratio_defense(tmp_path: Path) -> None:
    # 1MB of zeroes compresses into ~1000 bytes (>1000x ratio)
    zip_path = tmp_path / "bomb.zip"
    large_data = "0" * (1024 * 1024 * 2)  # 2MB repetitive text
    make_zip(zip_path, {"huge.txt": large_data})
    extractor = SafeArchiveExtractor(max_compression_ratio=50.0)
    with pytest.raises(ArchiveSecurityError, match="Compression ratio.*exceeds limit"):
        extractor._extract_zip(zip_path, tmp_path / "out")

def test_archive_total_size_threshold(tmp_path: Path) -> None:
    zip_path = tmp_path / "oversize.zip"
    make_zip(zip_path, {"file1.txt": "a" * 5000, "file2.txt": "b" * 5000})
    extractor = SafeArchiveExtractor(max_uncompressed_bytes=4000, max_compression_ratio=10000.0)
    with pytest.raises(ArchiveSecurityError, match="Uncompressed archive size.*exceeds limit"):
        extractor._extract_zip(zip_path, tmp_path / "out")

def test_single_file_size_limit(tmp_path: Path) -> None:
    zip_path = tmp_path / "big_single.zip"
    make_zip(zip_path, {"huge.json": "x" * 10000})
    extractor = SafeArchiveExtractor(max_single_file_bytes=2000, max_compression_ratio=10000.0)
    with pytest.raises(ArchiveSecurityError, match="exceeds maximum file limit"):
        extractor._extract_zip(zip_path, tmp_path / "out")
