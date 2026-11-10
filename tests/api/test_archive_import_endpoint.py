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
