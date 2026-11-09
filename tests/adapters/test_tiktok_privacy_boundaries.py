from __future__ import annotations

from sbh.adapters.tiktok import TikTokAdapter
from sbh.contracts.adapter import AccessOutcome


def test_tiktok_private_account_disclosure() -> None:
    adapter = TikTokAdapter()
    ok, limitation = adapter.check_privacy_boundary("@private_user")
    assert ok is False
    assert limitation is not None
    assert "private" in limitation.lower()


def test_tiktok_underage_account_disclosure() -> None:
    adapter = TikTokAdapter()
    page = adapter.lookup_account("@underage_user")
    assert page.outcome == AccessOutcome.REQUIRES_APPROVAL
    assert "minors" in str(page.limitation).lower()


def test_tiktok_public_account_allowed() -> None:
    adapter = TikTokAdapter()
    ok, limitation = adapter.check_privacy_boundary("@dance_creator")
    assert ok is True
    assert limitation is None
