from __future__ import annotations

from sbh.adapters.instagram import InstagramAdapter
from sbh.contracts.adapter import AccessOutcome
from sbh.contracts.platforms import Platform


def test_instagram_adapter_lookup_success() -> None:
    adapter = InstagramAdapter()
    page = adapter.lookup_account("creator_brand")
    assert page.outcome == AccessOutcome.OK
    assert len(page.items) == 1
    acc = page.items[0]
    assert acc.platform == Platform.INSTAGRAM
    assert acc.username == "creator_brand"
    assert acc.follower_count == 45000
    assert acc.following_count == 120
    assert acc.has_bio is True


def test_instagram_adapter_personal_user_boundary() -> None:
    adapter = InstagramAdapter()
    page = adapter.lookup_account("personal_user")
    assert page.outcome == AccessOutcome.REQUIRES_APPROVAL
    assert "personal/private" in str(page.limitation)


def test_instagram_adapter_content_and_fingerprints() -> None:
    adapter = InstagramAdapter()
    content_page = adapter.list_content("creator_brand", limit=10)
    assert content_page.outcome == AccessOutcome.OK
    assert len(content_page.items) == 2
    post = content_page.items[0]
    assert post.platform == Platform.INSTAGRAM
    assert post.simhash is not None
    assert len(post.simhash) == 16


def test_instagram_adapter_unsupported_graph_enumeration() -> None:
    adapter = InstagramAdapter()
    followers_page = adapter.list_followers("creator_brand")
    assert followers_page.outcome == AccessOutcome.REQUIRES_APPROVAL
    assert "follower list enumeration" in str(followers_page.limitation)

    following_page = adapter.list_following("creator_brand")
    assert following_page.outcome == AccessOutcome.REQUIRES_APPROVAL
