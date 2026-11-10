"""Security tests defending against directory traversal in archives."""

from __future__ import annotations

from pathlib import Path

import pytest
from tests.pipeline.archive_test_utils import make_tar, make_zip

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

def test_tar_path_traversal_relative(tmp_path: Path) -> None:
    tar_path = tmp_path / "traversal.tar.gz"
    make_tar(tar_path, {"../../../escape.txt": "evil"})
    extractor = SafeArchiveExtractor()
    with pytest.raises(ArchiveSecurityError, match="Directory traversal detected"):
        extractor._extract_tar(tar_path, tmp_path / "out")

def test_tar_symlink_rejection(tmp_path: Path) -> None:
    import tarfile
    tar_path = tmp_path / "symlink.tar"
    with tarfile.open(tar_path, "w") as tf:
        info = tarfile.TarInfo(name="link_to_root.txt")
        info.type = tarfile.SYMTYPE
        info.linkname = "/etc/passwd"
        tf.addfile(info)
    extractor = SafeArchiveExtractor()
    with pytest.raises(ArchiveSecurityError, match="Symlinks and hardlinks prohibited"):
        extractor._extract_tar(tar_path, tmp_path / "out")

def test_path_null_byte_rejection(tmp_path: Path) -> None:
    extractor = SafeArchiveExtractor()
    assert not extractor.is_safe_path(tmp_path, "file\x00name.txt")
    assert not extractor.is_safe_path(tmp_path, "C:\\Windows\\System32")
