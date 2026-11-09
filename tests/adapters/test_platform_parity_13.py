from __future__ import annotations

from sbh.adapters.instagram import InstagramAdapter
from sbh.adapters.tiktok import TikTokAdapter
from sbh.contracts.adapter import AccessOutcome
from sbh.contracts.platforms import Platform


def test_day09_granular_parity_check_13() -> None:
    ig = InstagramAdapter()
    tk = TikTokAdapter()

    assert ig.platform == Platform.INSTAGRAM
    assert tk.platform == Platform.TIKTOK

    # Verify followers always require approval across both platforms
    assert ig.list_followers("user").outcome == AccessOutcome.REQUIRES_APPROVAL
    assert tk.list_followers("user").outcome == AccessOutcome.REQUIRES_APPROVAL

    # Verify following always requires approval across both platforms
    assert ig.list_following("user").outcome == AccessOutcome.REQUIRES_APPROVAL
    assert tk.list_following("user").outcome == AccessOutcome.REQUIRES_APPROVAL
