"""Test utilities for creating synthetic valid and malicious test archives."""

from __future__ import annotations

import tarfile
import zipfile
from pathlib import Path


def make_zip(path: Path, entries: dict[str, str | bytes]) -> Path:
    """Create a ZIP archive with the specified entry names and contents."""
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, data in entries.items():
            if isinstance(data, str):
                zf.writestr(name, data.encode("utf-8"))
            else:
                zf.writestr(name, data)
    return path

def make_tar(path: Path, entries: dict[str, str | bytes], mode: str = "w:gz") -> Path:
    """Create a tarball archive with the specified entry names and contents."""
    import io
    with tarfile.open(path, mode) as tf:
        for name, data in entries.items():
            raw = data.encode("utf-8") if isinstance(data, str) else data
            info = tarfile.TarInfo(name=name)
            info.size = len(raw)
            tf.addfile(info, io.BytesIO(raw))
    return path
