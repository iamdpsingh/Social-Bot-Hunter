"""Security tests defending against directory traversal in archives."""

from __future__ import annotations

from pathlib import Path

import pytest
from tests.pipeline.archive_test_utils import make_zip

from sbh.pipeline.archive_ingest import ArchiveSecurityError, SafeArchiveExtractor


def test_zip_path_traversal_relative_parent(tmp_path: Path) -> None:
    zip_path = tmp_path / "traversal.zip"
    make_zip(zip_path, {"../../etc/passwd.txt": "evil"})
    extractor = SafeArchiveExtractor()
    with pytest.raises(ArchiveSecurityError, match="Directory traversal detected"):
        extractor._extract_zip(zip_path, tmp_path / "out")

def test_zip_path_traversal_absolute(tmp_path: Path) -> None:
    zip_path = tmp_path / "abs_traversal.zip"
    make_zip(zip_path, {"/tmp/hacked.txt": "evil"})
    extractor = SafeArchiveExtractor()
    with pytest.raises(ArchiveSecurityError, match="Directory traversal detected"):
        extractor._extract_zip(zip_path, tmp_path / "out")
