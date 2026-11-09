from __future__ import annotations

import pytest

from sbh.adapters.errors import InvalidUrlError
from sbh.adapters.url_validator import validate_profile_url


def test_tiktok_reserved_routes_rejection() -> None:
    reserved = ["@foryou", "@following", "@live", "@explore", "@tag", "@music", "@upload", "@about", "@legal"]
    for r in reserved:
        with pytest.raises(InvalidUrlError, match="reserved"):
            validate_profile_url(f"https://www.tiktok.com/{r}")
