"""Unit tests for archive resource quotas and boundary validation."""

from __future__ import annotations

from pathlib import Path

import pytest
from tests.pipeline.archive_test_utils import make_zip

from sbh.pipeline.archive_ingest import (
    ArchiveFormatError,
    ArchiveSecurityError,
    SafeArchiveExtractor,
)


def test_file_count_limit_exceeded(tmp_path: Path) -> None:
    zip_path = tmp_path / "many_files.zip"
    entries = {f"file_{i}.txt": "data" for i in range(10)}
    make_zip(zip_path, entries)
    extractor = SafeArchiveExtractor(max_files=5)
    with pytest.raises(ArchiveSecurityError, match="Archive file count exceeds maximum quota"):
        extractor._extract_zip(zip_path, tmp_path / "out")

def test_forbidden_file_extension(tmp_path: Path) -> None:
    zip_path = tmp_path / "executable.zip"
    make_zip(zip_path, {"script.sh": "echo evil", "data.json": "{}"})
    extractor = SafeArchiveExtractor()
    with pytest.raises(ArchiveSecurityError, match="Forbidden file extension"):
        extractor._extract_zip(zip_path, tmp_path / "out")

def test_empty_archive_rejection(tmp_path: Path) -> None:
    import zipfile
    zip_path = tmp_path / "empty.zip"
    with zipfile.ZipFile(zip_path, "w"):
        pass
    extractor = SafeArchiveExtractor()
    with pytest.raises(ArchiveFormatError, match="Archive contains no files"):
        extractor._extract_zip(zip_path, tmp_path / "out")
