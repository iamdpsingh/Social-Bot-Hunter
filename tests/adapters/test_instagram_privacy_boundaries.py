from __future__ import annotations

from sbh.adapters.instagram import InstagramAdapter
from sbh.contracts.adapter import AccessOutcome


def test_instagram_personal_account_disclosure() -> None:
    adapter = InstagramAdapter()
    ok, limitation = adapter.check_business_boundary("personal_user")
    assert ok is False
    assert limitation is not None
    assert "Business or Creator account" in limitation


def test_instagram_business_account_allowed() -> None:
    adapter = InstagramAdapter()
    ok, limitation = adapter.check_business_boundary("creator_brand")
    assert ok is True
    assert limitation is None


def test_instagram_media_without_raw_bytes() -> None:
    adapter = InstagramAdapter()
    page = adapter.list_content("creator_brand", limit=5)
    assert page.outcome == AccessOutcome.OK
    for post in page.items:
        # Data minimization: we store content id, length, simhash, but no raw binary blobs
        assert post.platform_content_id is not None
        assert post.simhash is not None
        assert not hasattr(post, "raw_media_bytes")
