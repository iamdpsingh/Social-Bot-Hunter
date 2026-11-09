from __future__ import annotations

from sbh.adapters.tiktok import TikTokAdapter
from sbh.contracts.adapter import AccessOutcome
from sbh.contracts.platforms import Platform


def test_tiktok_adapter_lookup_success() -> None:
    adapter = TikTokAdapter()
    page = adapter.lookup_account("@dance_creator")
    assert page.outcome == AccessOutcome.OK
    assert len(page.items) == 1
    acc = page.items[0]
    assert acc.platform == Platform.TIKTOK
    assert acc.username == "dance_creator"
    assert acc.follower_count == 185000
    assert acc.has_bio is True


def test_tiktok_adapter_private_account_boundary() -> None:
    adapter = TikTokAdapter()
    page = adapter.lookup_account("@private_user")
    assert page.outcome == AccessOutcome.REQUIRES_APPROVAL
    assert "private" in str(page.limitation)


def test_tiktok_adapter_content_and_fingerprints() -> None:
    adapter = TikTokAdapter()
    content_page = adapter.list_content("@dance_creator", limit=10)
    assert content_page.outcome == AccessOutcome.OK
    assert len(content_page.items) == 2
    video = content_page.items[0]
    assert video.platform == Platform.TIKTOK.value
    assert video.simhash is not None
    assert isinstance(video.simhash, int)


def test_tiktok_adapter_unsupported_graph_enumeration() -> None:
    adapter = TikTokAdapter()
    followers_page = adapter.list_followers("@dance_creator")
    assert followers_page.outcome == AccessOutcome.REQUIRES_APPROVAL
    assert "follower list enumeration" in str(followers_page.limitation)

    following_page = adapter.list_following("@dance_creator")
    assert following_page.outcome == AccessOutcome.REQUIRES_APPROVAL
