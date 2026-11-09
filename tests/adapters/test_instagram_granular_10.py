from __future__ import annotations

from sbh.adapters.instagram import InstagramAdapter
from sbh.adapters.instagram_client import MockInstagramClient
from sbh.contracts.adapter import AccessOutcome


def test_instagram_granular_case_10() -> None:
    client = MockInstagramClient()
    adapter = InstagramAdapter(client=client)

    # Verify query for known creator brand
    page = adapter.lookup_account("creator_brand")
    assert page.outcome == AccessOutcome.OK
    acc = page.items[0]
    assert acc.username == "creator_brand"
    assert acc.follower_count is not None and acc.follower_count > 0

    # Verify media list integrity
    content = adapter.list_content("creator_brand", limit=20)
    assert content.outcome == AccessOutcome.OK
    assert len(content.items) <= 20
