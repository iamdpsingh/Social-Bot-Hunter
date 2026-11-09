from __future__ import annotations

import pytest

from sbh.adapters.errors import InvalidUrlError
from sbh.adapters.url_validator import validate_profile_url


def test_instagram_reserved_routes_rejection() -> None:
    reserved = ["explore", "reels", "stories", "accounts", "direct", "developer", "about", "legal", "help", "api"]
    for r in reserved:
        with pytest.raises(InvalidUrlError, match="reserved"):
            validate_profile_url(f"https://www.instagram.com/{r}")
