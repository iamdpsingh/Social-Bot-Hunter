"""Tests for SSRF safety checks on input URLs."""

from __future__ import annotations

import pytest

from sbh.adapters.errors import InvalidUrlError
from sbh.adapters.url_validator import _validate_ssrf_safety


@pytest.mark.parametrize(
    "bad_url",
    [
        "http://localhost:8080/admin",
        "http://127.0.0.1/status",
        "http://169.254.169.254/latest/meta-data/",
        "http://10.0.0.1/internal",
        "http://192.168.1.1/router",
        "http://172.16.0.1/dashboard",
        "file:///etc/passwd",
        "javascript:alert(1)",
        "data:text/html;base64,PHNjcmlwdD4=",
        "ftp://files.example.com",
    ],
)
def test_ssrf_and_invalid_schemes_rejected(bad_url: str) -> None:
    with pytest.raises(InvalidUrlError):
        _validate_ssrf_safety(bad_url)


def test_url_length_limit() -> None:
    huge_url = "https://x.com/" + "a" * 2100
    with pytest.raises(InvalidUrlError, match="exceeds maximum length"):
        _validate_ssrf_safety(huge_url)
