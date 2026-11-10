from __future__ import annotations

import pytest

from sbh.adapters.errors import InvalidUrlError
from sbh.adapters.url_validator import UrlType, validate_profile_url
from sbh.contracts.platforms import Platform


def test_validate_linkedin_url_company_and_school() -> None:
    cases = [
        ("https://www.linkedin.com/company/tech-corp", "company:tech-corp", UrlType.CUSTOM_URL, True),
        ("https://linkedin.com/school/stanford-university", "school:stanford-university", UrlType.CUSTOM_URL, True),
        ("https://www.linkedin.com/in/satyanadella", "satyanadella", UrlType.HANDLE, True),
        ("https://www.linkedin.com/in/satyanadella?trk=feed", "satyanadella", UrlType.HANDLE, False),
    ]
    for raw_url, expected_handle, expected_type, expected_canonical in cases:
        info = validate_profile_url(raw_url, platform_hint=Platform.LINKEDIN)
        assert info.platform == Platform.LINKEDIN
        assert info.handle == expected_handle
        assert info.url_type == expected_type
        assert info.is_canonical == expected_canonical


def test_validate_linkedin_autodetection() -> None:
    info = validate_profile_url("https://www.linkedin.com/company/cyber-defense")
    assert info.platform == Platform.LINKEDIN
    assert info.handle == "company:cyber-defense"


def test_validate_linkedin_reserved_routes() -> None:
    reserved = ["feed", "jobs", "messaging", "notifications", "learning", "login", "signup", "help"]
    for r in reserved:
        with pytest.raises(InvalidUrlError, match="reserved"):
            validate_profile_url(f"https://www.linkedin.com/{r}")
