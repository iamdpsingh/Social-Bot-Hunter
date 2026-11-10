"""Integration tests for POST /api/v1/imports/archive."""

from __future__ import annotations

import pytest
from services.api.auth import require_investigator
from services.api.main import app


@pytest.fixture(autouse=True)
def investigator_auth_override() -> None:
    app.dependency_overrides[require_investigator] = lambda: {
        "id": "usr_investigator_1",
        "username": "investigator1",
        "role": "investigator",
    }
    yield
    app.dependency_overrides.pop(require_investigator, None)

def test_successful_zip_upload(tmp_path: Path) -> None:
    zip_path = tmp_path / "valid.zip"
    make_zip(zip_path, {"sample.json": '{"users": []}'})
    client = TestClient(app)
    with open(zip_path, "rb") as f:
        resp = client.post("/api/v1/imports/archive", files={"file": ("valid.zip", f, "application/zip")})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "extracted"
    assert data["file_count"] == 1
    assert data["archive_format"] == "generic_json"

def test_successful_tar_upload(tmp_path: Path) -> None:
    tar_path = tmp_path / "valid.tar.gz"
    make_tar(tar_path, {"records.csv": "col1,col2\n1,2\n"})
    client = TestClient(app)
    with open(tar_path, "rb") as f:
        resp = client.post("/api/v1/imports/archive", files={"file": ("valid.tar.gz", f, "application/gzip")})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "extracted"
    assert data["archive_format"] == "csv"

def test_detected_twitter_archive_upload(tmp_path: Path) -> None:
    zip_path = tmp_path / "twitter.zip"
    make_zip(zip_path, {"manifest.js": "{}", "data/tweet.js": "[]"})
    client = TestClient(app)
    with open(zip_path, "rb") as f:
        resp = client.post("/api/v1/imports/archive", files={"file": ("twitter.zip", f, "application/zip")})
    assert resp.status_code == 200
    data = resp.json()
    assert data["archive_format"] == "twitter_archive"
    assert data["platform_detected"] == "x"

def test_detected_ndjson_upload(tmp_path: Path) -> None:
    zip_path = tmp_path / "stream.zip"
    make_zip(zip_path, {"stream.ndjson": '{"user": "u1"}\n{"user": "u2"}\n'})
    client = TestClient(app)
    with open(zip_path, "rb") as f:
        resp = client.post("/api/v1/imports/archive", files={"file": ("stream.zip", f, "application/zip")})
    assert resp.status_code == 200
    data = resp.json()
    assert data["archive_format"] == "ndjson"

def test_detected_csv_upload(tmp_path: Path) -> None:
    zip_path = tmp_path / "dataset.zip"
    make_zip(zip_path, {"dataset.csv": "id,author\n100,bot1\n"})
    client = TestClient(app)
    with open(zip_path, "rb") as f:
        resp = client.post("/api/v1/imports/archive", files={"file": ("dataset.zip", f, "application/zip")})
    assert resp.status_code == 200
    data = resp.json()
    assert data["archive_format"] == "csv"

def test_upload_zip_bomb_rejection(tmp_path: Path) -> None:
    zip_path = tmp_path / "bomb.zip"
    make_zip(zip_path, {"huge.txt": "0" * (1024 * 1024 * 5)})
    client = TestClient(app)
    with open(zip_path, "rb") as f:
        resp = client.post("/api/v1/imports/archive", files={"file": ("bomb.zip", f, "application/zip")})
    assert resp.status_code == 400
    data = resp.json()
    assert data["detail"]["error"] == "security_violation"
    assert "Compression ratio" in data["detail"]["message"]

def test_upload_path_traversal_rejection(tmp_path: Path) -> None:
    zip_path = tmp_path / "traversal.zip"
    make_zip(zip_path, {"../../etc/passwd.txt": "evil"})
    client = TestClient(app)
    with open(zip_path, "rb") as f:
        resp = client.post("/api/v1/imports/archive", files={"file": ("traversal.zip", f, "application/zip")})
    assert resp.status_code == 400
    data = resp.json()
    assert data["detail"]["error"] == "security_violation"
    assert "Directory traversal" in data["detail"]["message"]

def test_upload_symlink_rejection(tmp_path: Path) -> None:
    import tarfile
    tar_path = tmp_path / "symlink.tar"
    with tarfile.open(tar_path, "w") as tf:
        info = tarfile.TarInfo(name="link.txt")
        info.type = tarfile.SYMTYPE
        info.linkname = "/etc/shadow"
        tf.addfile(info)
    client = TestClient(app)
    with open(tar_path, "rb") as f:
        resp = client.post("/api/v1/imports/archive", files={"file": ("symlink.tar", f, "application/x-tar")})
    assert resp.status_code == 400
    data = resp.json()
    assert data["detail"]["error"] == "security_violation"
    assert "Symlinks" in data["detail"]["message"]

def test_upload_forbidden_extension_rejection(tmp_path: Path) -> None:
    zip_path = tmp_path / "script.zip"
    make_zip(zip_path, {"malware.exe": "binary payload"})
    client = TestClient(app)
    with open(zip_path, "rb") as f:
        resp = client.post("/api/v1/imports/archive", files={"file": ("script.zip", f, "application/zip")})
    assert resp.status_code == 400
    data = resp.json()
    assert data["detail"]["error"] == "security_violation"
    assert "Forbidden file extension" in data["detail"]["message"]

def test_upload_empty_archive_rejection(tmp_path: Path) -> None:
    zip_path = tmp_path / "empty.zip"
    with zipfile.ZipFile(zip_path, "w"):
        pass
    client = TestClient(app)
    with open(zip_path, "rb") as f:
        resp = client.post("/api/v1/imports/archive", files={"file": ("empty.zip", f, "application/zip")})
    assert resp.status_code == 400
    data = resp.json()
    assert data["detail"]["error"] == "invalid_format"
    assert "contains no files" in data["detail"]["message"]

def test_upload_corrupt_archive_rejection(tmp_path: Path) -> None:
    corrupt_file = tmp_path / "corrupt.zip"
    corrupt_file.write_bytes(b"not a real zip file header garbage data")
    client = TestClient(app)
    with open(corrupt_file, "rb") as f:
        resp = client.post("/api/v1/imports/archive", files={"file": ("corrupt.zip", f, "application/zip")})
    assert resp.status_code == 400
    data = resp.json()
    assert data["detail"]["error"] == "invalid_format"
    assert "Unsupported or corrupted" in data["detail"]["message"]

def test_audit_log_entry_created(tmp_path: Path) -> None:
    zip_path = tmp_path / "audit_test.zip"
    make_zip(zip_path, {"sample.txt": "hello audit"})
    client = TestClient(app)
    with open(zip_path, "rb") as f:
        resp = client.post("/api/v1/imports/archive", files={"file": ("audit_test.zip", f, "application/zip")})
    assert resp.status_code == 200
    assert resp.json()["status"] == "extracted"
