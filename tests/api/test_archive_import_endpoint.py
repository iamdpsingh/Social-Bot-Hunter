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
