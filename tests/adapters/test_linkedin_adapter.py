from __future__ import annotations

from sbh.adapters.linkedin import LinkedInAdapter
from sbh.contracts.adapter import AccessOutcome
from sbh.contracts.platforms import Platform


def test_linkedin_adapter_lookup_org_success() -> None:
    adapter = LinkedInAdapter()
    page = adapter.lookup_account("company:tech_corp")
    assert page.outcome == AccessOutcome.OK
    assert len(page.items) == 1
    org = page.items[0]
    assert org.platform == Platform.LINKEDIN
    assert org.follower_count == 250000
    assert org.has_bio is True


def test_linkedin_adapter_lookup_member_success() -> None:
    adapter = LinkedInAdapter()
    page = adapter.lookup_account("satyanadella")
    assert page.outcome == AccessOutcome.OK
    assert len(page.items) == 1
    mem = page.items[0]
    assert mem.platform == Platform.LINKEDIN
    assert mem.display_name == "Satya Nadella"
    assert mem.is_verified is True


def test_linkedin_adapter_content_and_fingerprints() -> None:
    adapter = LinkedInAdapter()
    content_page = adapter.list_content("10001", limit=10)
    assert content_page.outcome == AccessOutcome.OK
    assert len(content_page.items) == 2
    post = content_page.items[0]
    assert post.platform == Platform.LINKEDIN.value
    assert post.simhash is not None
    assert isinstance(post.simhash, int)


def test_linkedin_adapter_unsupported_graph_enumeration() -> None:
    adapter = LinkedInAdapter()
    followers_page = adapter.list_followers("tech_corp")
    assert followers_page.outcome == AccessOutcome.REQUIRES_APPROVAL
    assert "follower list enumeration" in str(followers_page.limitation)

    following_page = adapter.list_following("tech_corp")
    assert following_page.outcome == AccessOutcome.REQUIRES_APPROVAL
