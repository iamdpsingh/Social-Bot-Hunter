from __future__ import annotations

from sbh.adapters.tiktok import TikTokAdapter
from sbh.adapters.tiktok_client import MockTikTokClient
from sbh.contracts.adapter import AccessOutcome


def test_tiktok_granular_case_07() -> None:
    client = MockTikTokClient()
    adapter = TikTokAdapter(client=client)

    # Verify lookup for active dance creator
    page = adapter.lookup_account("@dance_creator")
    assert page.outcome == AccessOutcome.OK
    acc = page.items[0]
    assert acc.username == "dance_creator"
    assert acc.following_count is not None and acc.following_count > 0

    # Verify video list query
    content = adapter.list_content("@dance_creator", limit=14)
    assert content.outcome == AccessOutcome.OK
    assert len(content.items) <= 14
