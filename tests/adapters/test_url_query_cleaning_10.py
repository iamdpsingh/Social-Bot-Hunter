from __future__ import annotations

from sbh.adapters.url_validator import validate_profile_url
from sbh.contracts.platforms import Platform


def test_url_query_cleaning_case_10() -> None:
    ig_raw = "https://www.instagram.com/verified_creator?igsh=sample_token_10&utm_medium=copy_link"
    ig_info = validate_profile_url(ig_raw)
    assert ig_info.platform == Platform.INSTAGRAM
    assert ig_info.handle == "verified_creator"
    assert ig_info.canonical_url == "https://www.instagram.com/verified_creator"
    assert ig_info.is_canonical is False

    tk_raw = "https://www.tiktok.com/@trend_setter?_t=sample_10&_r=1"
    tk_info = validate_profile_url(tk_raw)
    assert tk_info.platform == Platform.TIKTOK
    assert tk_info.handle == "@trend_setter"
    assert tk_info.canonical_url == "https://www.tiktok.com/@trend_setter"
    assert tk_info.is_canonical is False
