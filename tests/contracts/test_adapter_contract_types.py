"""Tests for PlatformAdapter protocol type verification."""

from __future__ import annotations

from sbh.contracts.adapter import AccessOutcome, NotConfiguredAdapter, Page, PlatformAdapter
from sbh.contracts.platforms import Platform


def test_not_configured_adapter_implements_protocol() -> None:
    adapter = NotConfiguredAdapter(Platform.YOUTUBE)
    assert isinstance(adapter, PlatformAdapter)
    assert adapter.platform == Platform.YOUTUBE


def test_page_exhausted_contract() -> None:
    page: Page[int] = Page(outcome=AccessOutcome.OK, items=(), next_cursor=None)
    assert page.outcome == AccessOutcome.OK
    assert len(page.items) == 0
    assert page.next_cursor is None
