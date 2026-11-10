"""Unit tests for archive resource quotas and boundary validation."""

from __future__ import annotations

from pathlib import Path

import pytest
from tests.pipeline.archive_test_utils import make_zip

from sbh.pipeline.archive_ingest import (
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
