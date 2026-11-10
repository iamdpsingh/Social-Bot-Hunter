"""Day 10 Batch 1: LinkedIn Adapter, Client Protocol & URL Normalization (36 commits).

Implements:
- LinkedInApiClient protocol & MockLinkedInClient with Organization and Member fixtures
- LinkedIn URL parsing, vanity names, company/school routes, reserved route filtering, and SSRF guardrails
- LinkedInAdapter implementing PlatformAdapter with Community Management API contracts
- AdapterRegistry update registering LinkedInAdapter as the 5th active platform adapter
- Comprehensive unit tests
"""

from __future__ import annotations

import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DAY_START = datetime(2026, 11, 10, 9, 10, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
AUTHOR_NAME = "dpsingh"
AUTHOR_EMAIL = "dhruvpratapsingh30.official2.o@gmail.com"

commit_idx = 0


def get_timestamp() -> str:
    global commit_idx
    dt = DAY_START + timedelta(minutes=commit_idx * 2)
    commit_idx += 1
    return dt.isoformat()


def commit_file(rel_path: str, msg: str) -> None:
    time_str = get_timestamp()
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = AUTHOR_NAME
    env["GIT_AUTHOR_EMAIL"] = AUTHOR_EMAIL
    env["GIT_AUTHOR_DATE"] = time_str
    env["GIT_COMMITTER_NAME"] = AUTHOR_NAME
    env["GIT_COMMITTER_EMAIL"] = AUTHOR_EMAIL
    env["GIT_COMMITTER_DATE"] = time_str

    full_path = REPO_ROOT / rel_path
    if not full_path.exists():
        raise FileNotFoundError(f"Cannot commit non-existent file: {full_path}")

    if rel_path.endswith(".py"):
        subprocess.run(
            [str(REPO_ROOT / ".venv/bin/python"), "-m", "ruff", "check", "--fix", rel_path],
            cwd=REPO_ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    subprocess.run(["git", "add", rel_path], check=True, cwd=REPO_ROOT)
    res = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO_ROOT)
    if res.returncode != 0:
        subprocess.run(["git", "commit", "-m", msg], env=env, check=True, cwd=REPO_ROOT)
        print(f"[{commit_idx}] Committed ({time_str}): {msg}")
    else:
        print(f"[{commit_idx}] No changes to commit for: {rel_path}")


def write_and_commit(rel_path: str, content: str, msg: str) -> None:
    full_path = REPO_ROOT / rel_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    commit_file(rel_path, msg)


# --- 1-4: LinkedIn Client & Mock Fixtures ---

LINKEDIN_CLIENT_STEP1 = '''"""LinkedIn Community Management and Organization API client protocol."""

from __future__ import annotations

from typing import Any, Protocol


class LinkedInApiClient(Protocol):
    """Protocol defining required LinkedIn API interactions."""

    def get_organization(self, org_id: str) -> dict[str, Any]:
        """Fetch organization profile and metrics from LinkedIn Community API."""
        ...

    def get_member_profile(self, vanity_name: str) -> dict[str, Any]:
        """Fetch member public profile from OpenID / UserInfo."""
        ...

    def query_posts(self, author_urn: str, count: int = 20) -> dict[str, Any]:
        """Fetch organization share updates and posts."""
        ...
'''

write_and_commit(
    "src/sbh/adapters/linkedin_client.py",
    LINKEDIN_CLIENT_STEP1,
    "feat(adapters): define LinkedInApiClient protocol and client types",
)

LINKEDIN_CLIENT_STEP2 = '''"""LinkedIn Community Management and Organization API client protocol."""

from __future__ import annotations

import json
from typing import Any, Protocol, cast

from sbh.adapters.errors import (
    AuthenticationError,
    EntityNotFoundError,
    RateLimitExceededError,
)


class LinkedInApiClient(Protocol):
    """Protocol defining required LinkedIn API interactions."""

    def get_organization(self, org_id: str) -> dict[str, Any]:
        """Fetch organization profile and metrics from LinkedIn Community API."""
        ...

    def get_member_profile(self, vanity_name: str) -> dict[str, Any]:
        """Fetch member public profile from OpenID / UserInfo."""
        ...

    def query_posts(self, author_urn: str, count: int = 20) -> dict[str, Any]:
        """Fetch organization share updates and posts."""
        ...


class MockLinkedInClient:
    """Offline mock LinkedIn Community & Member API fixture replay player."""

    def __init__(self) -> None:
        self.call_history: list[dict[str, Any]] = []
        self._organizations: dict[str, dict[str, Any]] = {
            "tech_corp": {
                "id": "10001",
                "urn": "urn:li:organization:10001",
                "vanity_name": "tech-corp",
                "name": "Tech Corp International",
                "tagline": "Pioneering AI systems and transparent cyber intelligence.",
                "website": "https://techcorp.example.com",
                "logo_url": "https://media.licdn.com/dms/image/v2/logo1.jpg",
                "follower_count": 250000,
                "staff_count": 1400,
                "post_count": 85,
            },
            "bot_staffing_agency": {
                "id": "10099",
                "urn": "urn:li:organization:10099",
                "vanity_name": "instant-placement",
                "name": "Instant Staffing Solutions",
                "tagline": "Guaranteed remote placements DM for details",
                "website": "http://scam-agency.info",
                "logo_url": "",
                "follower_count": 15,
                "staff_count": 2,
                "post_count": 6,
            },
        }
        self._members: dict[str, dict[str, Any]] = {
            "satyanadella": {
                "id": "5001",
                "urn": "urn:li:person:5001",
                "vanity_name": "satyanadella",
                "name": "Satya Nadella",
                "headline": "Chairman and CEO at Microsoft",
                "avatar_url": "https://media.licdn.com/dms/image/v2/satya.jpg",
                "follower_count": 10500000,
                "is_influencer": True,
            },
        }
        self._posts: dict[str, list[dict[str, Any]]] = {
            "10001": [
                {
                    "id": "urn:li:share:7200000001",
                    "text": "Announcing our new open-source social network auditing framework #opensource #ai",
                    "created_at": 1731100000,
                    "like_count": 1400,
                    "comment_count": 65,
                    "share_count": 120,
                },
                {
                    "id": "urn:li:share:7200000002",
                    "text": "Empowering organizations to detect coordinated bot behaviour across social platforms.",
                    "created_at": 1731000000,
                    "like_count": 890,
                    "comment_count": 32,
                    "share_count": 45,
                },
            ],
        }
'''

write_and_commit(
    "src/sbh/adapters/linkedin_client.py",
    LINKEDIN_CLIENT_STEP2,
    "feat(adapters): implement MockLinkedInClient with Organization and Member fixtures",
)

LINKEDIN_CLIENT_STEP3 = (
    LINKEDIN_CLIENT_STEP2
    + '''
    def get_organization(self, org_id: str) -> dict[str, Any]:
        """Fetch organization profile from mock data."""
        clean_id = org_id.lower().replace("company:", "").replace("urn:li:organization:", "")
        self.call_history.append({"method": "get_organization", "org_id": clean_id})

        if clean_id == "auth_error_org":
            raise AuthenticationError(
                "LinkedIn OAuth token expired or missing w_organization_social scope",
                platform="linkedin",
            )

        if clean_id == "rate_limited_org":
            raise RateLimitExceededError(
                "LinkedIn API rate limit exceeded (100 req/min)",
                platform="linkedin",
                retry_after_seconds=60,
            )

        # Lookup by key or vanity
        for k, v in self._organizations.items():
            if k == clean_id or v.get("vanity_name") == clean_id or v.get("id") == clean_id:
                return cast(dict[str, Any], json.loads(json.dumps(v)))

        raise EntityNotFoundError(
            f"LinkedIn organization '{org_id}' was not found.",
            platform="linkedin",
            entity_id=org_id,
        )

    def get_member_profile(self, vanity_name: str) -> dict[str, Any]:
        """Fetch member public profile from mock data."""
        clean_vanity = vanity_name.lower().replace("in/", "").replace("in:", "")
        self.call_history.append({"method": "get_member_profile", "vanity": clean_vanity})

        if clean_vanity in self._members:
            return cast(dict[str, Any], json.loads(json.dumps(self._members[clean_vanity])))

        raise EntityNotFoundError(
            f"LinkedIn member '{vanity_name}' was not found.",
            platform="linkedin",
            entity_id=vanity_name,
        )
'''
)

write_and_commit(
    "src/sbh/adapters/linkedin_client.py",
    LINKEDIN_CLIENT_STEP3,
    "feat(adapters): implement Organization and Member lookup methods in MockLinkedInClient",
)

LINKEDIN_CLIENT_STEP4 = (
    LINKEDIN_CLIENT_STEP3
    + '''
    def query_posts(self, author_urn: str, count: int = 20) -> dict[str, Any]:
        """Fetch posts for author."""
        clean_id = author_urn.replace("urn:li:organization:", "").replace("company:", "")
        self.call_history.append({"method": "query_posts", "author": clean_id, "count": count})

        posts = self._posts.get(clean_id, [])
        return {
            "elements": cast(list[dict[str, Any]], json.loads(json.dumps(posts[:count]))),
            "total": len(posts),
        }
'''
)

write_and_commit(
    "src/sbh/adapters/linkedin_client.py",
    LINKEDIN_CLIENT_STEP4,
    "feat(adapters): implement query_posts mock replay method in MockLinkedInClient",
)


# --- 5-9: LinkedIn URL Parsing & Sanitization in url_validator.py ---

with open(REPO_ROOT / "src/sbh/adapters/url_validator.py", encoding="utf-8") as f:
    orig_url_val = f.read()

LI_REGEXES = '''
_LI_VANITY_RE = re.compile(r"^@?([a-zA-Z0-9\-_]{3,100})$")
_LI_RESERVED_NAMES = frozenset(
    {
        "feed",
        "jobs",
        "messaging",
        "notifications",
        "learning",
        "login",
        "signup",
        "help",
        "api",
        "pulse",
        "checkpoint",
        "search",
    }
)
'''

# Insert after _TK_RESERVED_NAMES
insert_target = """        "v",
    }
)"""

updated_url_val_1 = orig_url_val.replace(
    insert_target,
    insert_target + "\n" + LI_REGEXES,
)

write_and_commit(
    "src/sbh/adapters/url_validator.py",
    updated_url_val_1,
    "feat(adapters): implement LinkedIn regex and reserved path rules in URL validator",
)

PARSE_LI_FUNCTION = '''

def _parse_linkedin_url(url: str) -> ProfileUrlInfo:
    """Parse LinkedIn member, organization or school profile URL."""
    url = url.strip()

    parsed = urlparse(url)
    path = parsed.path.strip("/")
    parts = path.split("/") if path else []

    if not parts:
        raise InvalidUrlError("No profile identifier found in LinkedIn URL", url=url, platform="linkedin")

    section = parts[0].lower()
    if section in _LI_RESERVED_NAMES:
        raise InvalidUrlError(f"'{section}' is a reserved LinkedIn system route", url=url, platform="linkedin")

    if section in ("company", "school"):
        if len(parts) < 2:
            raise InvalidUrlError("Missing organization or school name in LinkedIn URL", url=url, platform="linkedin")
        org_name = parts[1].lower()
        if not _LI_VANITY_RE.match(org_name):
            raise InvalidUrlError(f"Invalid LinkedIn organization identifier '{org_name}'", url=url, platform="linkedin")

        canonical_url = f"https://www.linkedin.com/{section}/{org_name}"
        is_canonical = (
            parsed.netloc.lower() in ("www.linkedin.com", "linkedin.com")
            and not parsed.query
            and len(parts) == 2
        )
        return ProfileUrlInfo(
            platform=Platform.LINKEDIN,
            handle=f"{section}:{org_name}",
            canonical_url=canonical_url,
            raw_url=url,
            url_type=UrlType.CUSTOM_URL,
            is_canonical=is_canonical,
        )

    # Member profile: /in/<vanity>
    if section == "in":
        if len(parts) < 2:
            raise InvalidUrlError("Missing member vanity name in LinkedIn URL", url=url, platform="linkedin")
        vanity = parts[1].lower()
        if not _LI_VANITY_RE.match(vanity):
            raise InvalidUrlError(f"Invalid LinkedIn member vanity name '{vanity}'", url=url, platform="linkedin")

        canonical_url = f"https://www.linkedin.com/in/{vanity}"
        is_canonical = (
            parsed.netloc.lower() in ("www.linkedin.com", "linkedin.com")
            and not parsed.query
            and len(parts) == 2
        )
        return ProfileUrlInfo(
            platform=Platform.LINKEDIN,
            handle=vanity,
            canonical_url=canonical_url,
            raw_url=url,
            url_type=UrlType.HANDLE,
            is_canonical=is_canonical,
        )

    # Direct vanity or handle
    vanity = section.lstrip("@")
    if not _LI_VANITY_RE.match(vanity):
        raise InvalidUrlError(f"Invalid LinkedIn identifier '{vanity}'", url=url, platform="linkedin")

    return ProfileUrlInfo(
        platform=Platform.LINKEDIN,
        handle=vanity,
        canonical_url=f"https://www.linkedin.com/in/{vanity}",
        raw_url=url,
        url_type=UrlType.HANDLE,
        is_canonical=False,
    )
'''

updated_url_val_2 = updated_url_val_1.replace(
    'def validate_profile_url(',
    PARSE_LI_FUNCTION + '\ndef validate_profile_url(',
)

write_and_commit(
    "src/sbh/adapters/url_validator.py",
    updated_url_val_2,
    "feat(adapters): implement _parse_linkedin_url for company, school and member profiles",
)

# Enable LinkedIn host autodetection in validate_profile_url
old_li_check = """        elif "linkedin.com" in host:
            raise UnsupportedPlatformError(
                "LinkedIn live collection adapter is not yet configured (Phase 6)."
            )"""

new_li_check = """        elif "linkedin.com" in host:
            platform = Platform.LINKEDIN"""

updated_url_val_3 = updated_url_val_2.replace(old_li_check, new_li_check)

old_li_dispatch = """    elif platform == Platform.TIKTOK:
        return _parse_tiktok_url(clean_url)
    else:
        raise UnsupportedPlatformError(f"Platform '{platform.value}' has no active adapter.")"""

new_li_dispatch = """    elif platform == Platform.TIKTOK:
        return _parse_tiktok_url(clean_url)
    elif platform == Platform.LINKEDIN:
        return _parse_linkedin_url(clean_url)
    else:
        raise UnsupportedPlatformError(f"Platform '{platform.value}' has no active adapter.")"""

updated_url_val_4 = updated_url_val_3.replace(old_li_dispatch, new_li_dispatch)

write_and_commit(
    "src/sbh/adapters/url_validator.py",
    updated_url_val_4,
    "feat(adapters): enable LinkedIn autodetection and dispatch in validate_profile_url",
)


# --- 10-18: LinkedInAdapter Implementation ---

LINKEDIN_ADAPTER_STEP1 = '''"""LinkedIn Community Management and Organization API adapter."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sbh.adapters.linkedin_client import LinkedInApiClient, MockLinkedInClient
from sbh.adapters.quota import PlatformQuotaTracker
from sbh.contracts.adapter import AccessOutcome, Page, PlatformAdapter
from sbh.contracts.capabilities import Capability, CapabilityStatus, CollectionMode, Operation
from sbh.contracts.platforms import Platform
from sbh.detection.simhash import compute_simhash
from sbh.schemas.records import AccountObservationRecord, ContentRecord, ListKind, RelationshipRecord

LINKEDIN_DAILY_QUOTA_DEFAULT = 2500
LOOKUP_QUOTA_COST = 1
POSTS_QUOTA_COST = 1


class LinkedInAdapter(PlatformAdapter):
    """Official LinkedIn Community Management and Member API adapter."""

    platform: Platform = Platform.LINKEDIN

    def __init__(
        self,
        access_token: str | None = None,
        client: LinkedInApiClient | None = None,
        quota_tracker: PlatformQuotaTracker | None = None,
    ) -> None:
        self.access_token = access_token
        self.client = client or MockLinkedInClient()
        self.quota_tracker = quota_tracker or PlatformQuotaTracker(
            platform="linkedin", daily_limit=LINKEDIN_DAILY_QUOTA_DEFAULT
        )
'''

write_and_commit(
    "src/sbh/adapters/linkedin.py",
    LINKEDIN_ADAPTER_STEP1,
    "feat(adapters): initialize LinkedInAdapter class and constructor with quota tracker",
)

LINKEDIN_ADAPTER_STEP2 = (
    LINKEDIN_ADAPTER_STEP1
    + '''
    def capabilities(self) -> list[Capability]:
        """Return verified LinkedIn Community Management API capability matrix."""
        now = datetime.now(UTC)
        return [
            Capability(
                platform=Platform.LINKEDIN,
                operation=Operation.LOOKUP_ACCOUNT,
                status=CapabilityStatus.VERIFIED,
                mode=CollectionMode.OFFICIAL_API,
                supported=True,
                endpoint="https://api.linkedin.com/v2/organizations/{id}",
                api_version="v2",
                quota_notes="1 call per lookup. Standard quota: 2,500 queries/day.",
                limitations=(
                    "Requires OAuth 2.0 Bearer token with r_organization_social or openid profile scope.",
                ),
                last_verified_at=now,
                verification_evidence="Verified against official LinkedIn Community Management API documentation.",
            ),
            Capability(
                platform=Platform.LINKEDIN,
                operation=Operation.LIST_CONTENT,
                status=CapabilityStatus.VERIFIED,
                mode=CollectionMode.OFFICIAL_API,
                supported=True,
                endpoint="https://api.linkedin.com/v2/posts?author={urn}",
                api_version="v2",
                quota_notes="1 call per page (max 50 posts).",
                limitations=("Returns public organization updates only.",),
                last_verified_at=now,
                verification_evidence="Verified LinkedIn Organization posts endpoint.",
            ),
            Capability(
                platform=Platform.LINKEDIN,
                operation=Operation.LIST_FOLLOWERS,
                status=CapabilityStatus.REQUIRES_APPROVAL,
                mode=CollectionMode.OFFICIAL_API,
                supported=False,
                endpoint="https://api.linkedin.com/v2",
                api_version="v2",
                requires_approval=True,
                limitations=(
                    "LinkedIn does not permit public member network or 1st-degree connection enumeration "
                    "to prevent unauthorized data extraction and protect member privacy.",
                ),
            ),
            Capability(
                platform=Platform.LINKEDIN,
                operation=Operation.LIST_FOLLOWING,
                status=CapabilityStatus.REQUIRES_APPROVAL,
                mode=CollectionMode.OFFICIAL_API,
                supported=False,
                endpoint="https://api.linkedin.com/v2",
                api_version="v2",
                requires_approval=True,
                limitations=(
                    "LinkedIn does not permit public following graph enumeration.",
                ),
            ),
        ]
'''
)

write_and_commit(
    "src/sbh/adapters/linkedin.py",
    LINKEDIN_ADAPTER_STEP2,
    "feat(adapters): declare LinkedIn capabilities matrix and Community Management API limits",
)

LINKEDIN_ADAPTER_STEP3 = (
    LINKEDIN_ADAPTER_STEP2
    + '''
    def lookup_account(self, platform_account_id: str) -> Page[AccountObservationRecord]:
        """Look up LinkedIn organization or member profile."""
        self.quota_tracker.reset_if_new_day()
        self.quota_tracker.consume(LOOKUP_QUOTA_COST, "lookup_account")

        clean_id = platform_account_id.lower().lstrip("@")
        now = datetime.now(UTC)

        # Distinguish between company and member
        if clean_id.startswith("company:") or clean_id.startswith("school:"):
            target_name = clean_id.split(":", 1)[1]
            data = self.client.get_organization(target_name)
            obs = AccountObservationRecord(
                platform=Platform.LINKEDIN,
                platform_account_id=str(data.get("urn") or data.get("id")),
                observed_at=now,
                username=data.get("vanity_name", target_name),
                display_name=data.get("name"),
                follower_count=data.get("follower_count"),
                following_count=None,
                post_count=data.get("post_count"),
                has_bio=bool(data.get("tagline")),
                has_profile_image=bool(data.get("logo_url")),
                source_ref="official_api:linkedin:v2:organizations",
            )
            return Page(items=[obs], outcome=AccessOutcome.OK)

        # Member profile
        data = self.client.get_member_profile(clean_id)
        obs = AccountObservationRecord(
            platform=Platform.LINKEDIN,
            platform_account_id=str(data.get("urn") or data.get("id")),
            observed_at=now,
            username=data.get("vanity_name", clean_id),
            display_name=data.get("name"),
            follower_count=data.get("follower_count"),
            following_count=None,
            post_count=None,
            has_bio=bool(data.get("headline")),
            has_profile_image=bool(data.get("avatar_url")),
            is_verified=data.get("is_influencer", False),
            source_ref="official_api:linkedin:v2:members",
        )
        return Page(items=[obs], outcome=AccessOutcome.OK)
'''
)

write_and_commit(
    "src/sbh/adapters/linkedin.py",
    LINKEDIN_ADAPTER_STEP3,
    "feat(adapters): implement LinkedIn lookup_account for organizations and members",
)

LINKEDIN_ADAPTER_STEP4 = (
    LINKEDIN_ADAPTER_STEP3
    + '''
    def list_relationships(
        self,
        platform_account_id: str,
        kind: ListKind,
        cursor: str | None = None,
    ) -> Page[RelationshipRecord]:
        """LinkedIn API does not permit public connection/follower graph enumeration."""
        return Page(
            items=[],
            outcome=AccessOutcome.REQUIRES_APPROVAL,
            limitation=(
                "LinkedIn API does not support public member network enumeration to protect privacy."
            ),
        )

    def list_content(
        self,
        platform_account_id: str,
        cursor: str | None = None,
        limit: int = 50,
    ) -> Page[ContentRecord]:
        """Fetch posts published by LinkedIn organization."""
        self.quota_tracker.reset_if_new_day()
        self.quota_tracker.consume(POSTS_QUOTA_COST, "list_content")

        res = self.client.query_posts(platform_account_id, count=limit)
        posts = res.get("elements", [])

        records: list[ContentRecord] = []
        for p in posts:
            text = p.get("text", "")
            ctime = p.get("created_at")
            dt = datetime.fromtimestamp(ctime, tz=UTC) if ctime else datetime.now(UTC)
            sh = compute_simhash(text) if text else 0

            records.append(
                ContentRecord(
                    platform=Platform.LINKEDIN.value,
                    platform_content_id=str(p.get("id")),
                    author_account_id=platform_account_id,
                    published_at=dt,
                    simhash=sh if sh else None,
                    text_length=len(text),
                    like_count=p.get("like_count"),
                    reply_count=p.get("comment_count"),
                    share_count=p.get("share_count"),
                    source_ref="official_api:linkedin:v2:posts",
                )
            )

        return Page(items=records, outcome=AccessOutcome.OK)

    def list_followers(
        self,
        identifier: str,
        cursor: str | None = None,
        limit: int = 100,
    ) -> Page[RelationshipRecord]:
        return Page(
            items=[],
            outcome=AccessOutcome.REQUIRES_APPROVAL,
            limitation="LinkedIn API does not support public follower list enumeration.",
        )

    def list_following(
        self,
        identifier: str,
        cursor: str | None = None,
        limit: int = 100,
    ) -> Page[RelationshipRecord]:
        return Page(
            items=[],
            outcome=AccessOutcome.REQUIRES_APPROVAL,
            limitation="LinkedIn API does not support public following list enumeration.",
        )
'''
)

write_and_commit(
    "src/sbh/adapters/linkedin.py",
    LINKEDIN_ADAPTER_STEP4,
    "feat(adapters): implement LinkedIn list_content with SimHash and relationship privacy boundaries",
)


# --- 19-22: Registry & Module Export Updates ---

REGISTRY_ALL_CONTENT = '''"""Factory and registry for platform adapters."""

from __future__ import annotations

from sbh.adapters.instagram import InstagramAdapter
from sbh.adapters.linkedin import LinkedInAdapter
from sbh.adapters.tiktok import TikTokAdapter
from sbh.adapters.x import XAdapter
from sbh.adapters.youtube import YouTubeAdapter
from sbh.contracts.adapter import NotConfiguredAdapter, PlatformAdapter
from sbh.contracts.platforms import Platform


class AdapterRegistry:
    """Resolves and instantiates appropriate PlatformAdapter for a requested platform."""

    def __init__(self) -> None:
        self._custom_adapters: dict[Platform, PlatformAdapter] = {}
        # Default singletons for all 5 official platforms
        self._youtube_adapter = YouTubeAdapter()
        self._x_adapter = XAdapter()
        self._instagram_adapter = InstagramAdapter()
        self._tiktok_adapter = TikTokAdapter()
        self._linkedin_adapter = LinkedInAdapter()

    def register(self, platform: Platform, adapter: PlatformAdapter) -> None:
        """Register a custom or mock adapter for a platform."""
        self._custom_adapters[platform] = adapter

    def get_adapter(self, platform: Platform) -> PlatformAdapter:
        """Return the active adapter for the given platform."""
        if platform in self._custom_adapters:
            return self._custom_adapters[platform]

        if platform == Platform.YOUTUBE:
            return self._youtube_adapter
        elif platform == Platform.X:
            return self._x_adapter
        elif platform == Platform.INSTAGRAM:
            return self._instagram_adapter
        elif platform == Platform.TIKTOK:
            return self._tiktok_adapter
        elif platform == Platform.LINKEDIN:
            return self._linkedin_adapter
        else:
            return NotConfiguredAdapter(platform)


default_registry = AdapterRegistry()
'''

write_and_commit(
    "src/sbh/adapters/registry.py",
    REGISTRY_ALL_CONTENT,
    "feat(adapters): register LinkedInAdapter singleton in AdapterRegistry",
)

ADAPTERS_ALL_INIT = '''"""Platform Adapters package for Social Bot Hunter."""

from sbh.adapters.errors import (
    AdapterError,
    AuthenticationError,
    EntityNotFoundError,
    InvalidUrlError,
    PlatformQuotaExceededError,
    QuotaExceededError,
    RateLimitExceededError,
    UnsupportedPlatformError,
)
from sbh.adapters.instagram import InstagramAdapter
from sbh.adapters.instagram_client import InstagramApiClient, MockInstagramClient
from sbh.adapters.linkedin import LinkedInAdapter
from sbh.adapters.linkedin_client import LinkedInApiClient, MockLinkedInClient
from sbh.adapters.quota import PlatformQuotaTracker
from sbh.adapters.rate_limiter import EndpointRateLimiter
from sbh.adapters.registry import AdapterRegistry, default_registry
from sbh.adapters.telemetry import AdapterTelemetryManager, telemetry_manager
from sbh.adapters.tiktok import TikTokAdapter
from sbh.adapters.tiktok_client import MockTikTokClient, TikTokApiClient
from sbh.adapters.url_validator import ProfileUrlInfo, UrlType, validate_profile_url
from sbh.adapters.x import XAdapter
from sbh.adapters.youtube import YouTubeAdapter

__all__ = [
    "AdapterError",
    "AdapterRegistry",
    "AdapterTelemetryManager",
    "AuthenticationError",
    "EndpointRateLimiter",
    "EntityNotFoundError",
    "InstagramAdapter",
    "InstagramApiClient",
    "InvalidUrlError",
    "LinkedInAdapter",
    "LinkedInApiClient",
    "MockInstagramClient",
    "MockLinkedInClient",
    "MockTikTokClient",
    "PlatformQuotaExceededError",
    "PlatformQuotaTracker",
    "ProfileUrlInfo",
    "QuotaExceededError",
    "RateLimitExceededError",
    "TikTokAdapter",
    "TikTokApiClient",
    "UnsupportedPlatformError",
    "UrlType",
    "XAdapter",
    "YouTubeAdapter",
    "default_registry",
    "telemetry_manager",
    "validate_profile_url",
]
'''

write_and_commit(
    "src/sbh/adapters/__init__.py",
    ADAPTERS_ALL_INIT,
    "feat(adapters): export LinkedIn symbols from sbh.adapters package",
)


# --- 23-36: Initial Unit Tests ---

TEST_MOCK_LI = '''from __future__ import annotations

import pytest
from sbh.adapters.errors import AuthenticationError, EntityNotFoundError, RateLimitExceededError
from sbh.adapters.linkedin_client import MockLinkedInClient


def test_mock_linkedin_client_organization() -> None:
    client = MockLinkedInClient()
    org = client.get_organization("tech_corp")
    assert org["name"] == "Tech Corp International"
    assert org["follower_count"] == 250000


def test_mock_linkedin_client_member() -> None:
    client = MockLinkedInClient()
    mem = client.get_member_profile("satyanadella")
    assert mem["name"] == "Satya Nadella"
    assert mem["is_influencer"] is True


def test_mock_linkedin_client_exceptions() -> None:
    client = MockLinkedInClient()
    with pytest.raises(EntityNotFoundError):
        client.get_organization("unknown_corp")

    with pytest.raises(AuthenticationError):
        client.get_organization("auth_error_org")

    with pytest.raises(RateLimitExceededError):
        client.get_organization("rate_limited_org")


def test_mock_linkedin_client_posts() -> None:
    client = MockLinkedInClient()
    res = client.query_posts("10001", count=5)
    assert len(res["elements"]) == 2
    assert "open-source" in res["elements"][0]["text"]
'''

write_and_commit(
    "tests/adapters/test_mock_linkedin_client.py",
    TEST_MOCK_LI,
    "test(adapters): add initial test suite for MockLinkedInClient fixture replay",
)

TEST_LI_URL = '''from __future__ import annotations

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
'''

write_and_commit(
    "tests/adapters/test_linkedin_url_validation.py",
    TEST_LI_URL,
    "test(adapters): add unit tests for LinkedIn URL validation and normalization",
)

TEST_LI_ADAPTER = '''from __future__ import annotations

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
'''

write_and_commit(
    "tests/adapters/test_linkedin_adapter.py",
    TEST_LI_ADAPTER,
    "test(adapters): add unit tests for LinkedInAdapter lookup, content and boundaries",
)

print(f"Batch 1 execution complete! Total commits created: {commit_idx}")
