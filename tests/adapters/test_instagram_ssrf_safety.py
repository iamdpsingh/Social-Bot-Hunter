from __future__ import annotations

import pytest

from sbh.adapters.errors import InvalidUrlError
from sbh.adapters.url_validator import validate_profile_url
from sbh.contracts.platforms import Platform


def test_instagram_ssrf_forbidden_hostnames() -> None:
    forbidden = [
        "http://localhost/instagram_user",
        "http://127.0.0.1/instagram_user",
        "http://169.254.169.254/instagram_user",
    ]
    for url in forbidden:
        with pytest.raises(InvalidUrlError, match="rejected for security|Private IP"):
            validate_profile_url(url, platform_hint=Platform.INSTAGRAM)
