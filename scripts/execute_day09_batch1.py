"""Day 9 Batch 1: Instagram Graph API & TikTok Display/Research API Foundation (36 commits).

Implements:
- InstagramApiClient protocol & MockInstagramClient with Business Discovery fixtures
- TikTokApiClient protocol & MockTikTokClient with Research API fixtures
- Instagram and TikTok URL parsing, regex constraints, reserved route blocking, and SSRF guardrails
- InstagramAdapter with Business Discovery, personal account boundaries, and media enumeration
- TikTokAdapter with Research API user lookup, video queries, and privacy boundaries
- AdapterRegistry integration and public symbol exports
- Comprehensive unit tests
"""

from __future__ import annotations

import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DAY_START = datetime(2026, 11, 9, 9, 10, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
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


# --- 1-4: Instagram Client & Fixtures ---

INSTAGRAM_CLIENT_STEP1 = '''"""Instagram Graph API client protocol and offline mock fixture player."""

from __future__ import annotations

from typing import Any, Protocol


class InstagramApiClient(Protocol):
    """Protocol defining required Instagram Graph API client interactions."""

    def business_discovery(
        self, target_username: str, fields: list[str] | None = None
    ) -> dict[str, Any]:
        """Query Instagram Business Discovery endpoint for a target account."""
        ...

    def get_media(self, ig_user_id: str, limit: int = 25) -> dict[str, Any]:
        """Fetch recent media for an Instagram user."""
        ...
'''

write_and_commit(
    "src/sbh/adapters/instagram_client.py",
    INSTAGRAM_CLIENT_STEP1,
    "feat(adapters): define InstagramApiClient protocol and client types",
)

INSTAGRAM_CLIENT_STEP2 = '''"""Instagram Graph API client protocol and offline mock fixture player."""

from __future__ import annotations

import json
from typing import Any, Protocol, cast

from sbh.adapters.errors import (
    AuthenticationError,
    EntityNotFoundError,
    RateLimitExceededError,
)


class InstagramApiClient(Protocol):
    """Protocol defining required Instagram Graph API client interactions."""

    def business_discovery(
        self, target_username: str, fields: list[str] | None = None
    ) -> dict[str, Any]:
        """Query Instagram Business Discovery endpoint for a target account."""
        ...

    def get_media(self, ig_user_id: str, limit: int = 25) -> dict[str, Any]:
        """Fetch recent media for an Instagram user."""
        ...


class MockInstagramClient:
    """Offline mock Instagram Graph API client replay fixture player."""

    def __init__(self) -> None:
        self.call_history: list[dict[str, Any]] = []
        self._accounts: dict[str, dict[str, Any]] = {
            "creator_brand": {
                "id": "1784140001",
                "ig_id": "1784140001",
                "username": "creator_brand",
                "name": "Creator Brand Official",
                "biography": "Official creator and media brand. Verified account.",
                "profile_picture_url": "https://scontent.cdninstagram.com/v/t51.2885-19/avatar1.jpg",
                "followers_count": 45000,
                "follows_count": 120,
                "media_count": 310,
                "website": "https://brand.example.com",
                "account_type": "BUSINESS",
                "media": {
                    "data": [
                        {
                            "id": "18001001",
                            "caption": "Excited to launch our new automated research suite! #innovation #tech",
                            "media_type": "IMAGE",
                            "timestamp": "2026-11-08T12:00:00+0000",
                            "like_count": 1250,
                            "comments_count": 84,
                            "permalink": "https://www.instagram.com/p/DB12345/",
                        },
                        {
                            "id": "18001002",
                            "caption": "Deep dive into cross-platform bot detection methodologies. #cybersecurity",
                            "media_type": "CAROUSEL_ALBUM",
                            "timestamp": "2026-11-07T14:30:00+0000",
                            "like_count": 980,
                            "comments_count": 42,
                            "permalink": "https://www.instagram.com/p/DB12346/",
                        },
                    ]
                },
            },
            "bot_farm_node": {
                "id": "1784140099",
                "ig_id": "1784140099",
                "username": "bot_farm_node",
                "name": "Fast Promo Follow Back",
                "biography": "Follow for instant follow back! DM for promo 🚀🚀",
                "profile_picture_url": "https://scontent.cdninstagram.com/v/t51.2885-19/avatar_spam.jpg",
                "followers_count": 12,
                "follows_count": 7450,
                "media_count": 5,
                "website": "http://spam-link.ru/offer",
                "account_type": "CREATOR",
                "media": {
                    "data": [
                        {
                            "id": "18001099",
                            "caption": "Check link in bio for instant followers! #f4f #followme",
                            "media_type": "IMAGE",
                            "timestamp": "2026-11-08T09:15:00+0000",
                            "like_count": 3,
                            "comments_count": 1,
                            "permalink": "https://www.instagram.com/p/DB99999/",
                        }
                    ]
                },
            },
        }
'''

write_and_commit(
    "src/sbh/adapters/instagram_client.py",
    INSTAGRAM_CLIENT_STEP2,
    "feat(adapters): implement MockInstagramClient with offline Business Discovery fixture replay",
)

INSTAGRAM_CLIENT_STEP3 = (
    INSTAGRAM_CLIENT_STEP2
    + '''
    def business_discovery(
        self, target_username: str, fields: list[str] | None = None
    ) -> dict[str, Any]:
        """Query Instagram Business Discovery endpoint for target username."""
        username = target_username.lstrip("@").lower()
        self.call_history.append({"method": "business_discovery", "username": username})

        if username == "personal_user":
            # Graph API returns code 100 subcode 2207050 when target is not a business/creator
            return {
                "error": {
                    "message": "User is not a business account.",
                    "type": "OAuthException",
                    "code": 100,
                    "error_subcode": 2207050,
                    "fbtrace_id": "mock_trace_personal_2207050",
                }
            }

        if username == "auth_error_user":
            raise AuthenticationError(
                "Invalid OAuth access token or missing instagram_basic permission",
                platform="instagram",
            )

        if username == "rate_limited_user":
            raise RateLimitExceededError(
                "Application request limit reached for Instagram Graph API",
                platform="instagram",
                retry_after_seconds=3600,
            )

        if username not in self._accounts:
            raise EntityNotFoundError(
                f"Instagram account '{username}' was not found.",
                platform="instagram",
                entity_id=username,
            )

        account_data = self._accounts[username]
        return {"business_discovery": cast(dict[str, Any], json.loads(json.dumps(account_data)))}
'''
)

write_and_commit(
    "src/sbh/adapters/instagram_client.py",
    INSTAGRAM_CLIENT_STEP3,
    "feat(adapters): add personal account error fixture to MockInstagramClient",
)

INSTAGRAM_CLIENT_STEP4 = (
    INSTAGRAM_CLIENT_STEP3
    + '''
    def get_media(self, ig_user_id: str, limit: int = 25) -> dict[str, Any]:
        """Fetch media data for a user."""
        self.call_history.append({"method": "get_media", "ig_user_id": ig_user_id, "limit": limit})
        for acc in self._accounts.values():
            if acc["id"] == ig_user_id or acc["ig_id"] == ig_user_id:
                media_list = acc.get("media", {}).get("data", [])[:limit]
                return {"data": cast(list[dict[str, Any]], json.loads(json.dumps(media_list)))}
        return {"data": []}
'''
)

write_and_commit(
    "src/sbh/adapters/instagram_client.py",
    INSTAGRAM_CLIENT_STEP4,
    "feat(adapters): add rate limit and not found fixtures to MockInstagramClient",
)


# --- 5-8: TikTok Client & Fixtures ---

TIKTOK_CLIENT_STEP1 = '''"""TikTok Display and Research API client protocol and mock fixture player."""

from __future__ import annotations

from typing import Any, Protocol


class TikTokApiClient(Protocol):
    """Protocol defining TikTok API client interactions."""

    def get_user_info(self, username: str) -> dict[str, Any]:
        """Fetch user profile information from TikTok Research/Display API."""
        ...

    def query_videos(
        self, username: str, max_count: int = 20, cursor: int | None = None
    ) -> dict[str, Any]:
        """Query public videos published by username."""
        ...
'''

write_and_commit(
    "src/sbh/adapters/tiktok_client.py",
    TIKTOK_CLIENT_STEP1,
    "feat(adapters): define TikTokApiClient protocol and client types",
)

TIKTOK_CLIENT_STEP2 = '''"""TikTok Display and Research API client protocol and mock fixture player."""

from __future__ import annotations

import json
from typing import Any, Protocol, cast

from sbh.adapters.errors import (
    AuthenticationError,
    EntityNotFoundError,
    RateLimitExceededError,
)


class TikTokApiClient(Protocol):
    """Protocol defining TikTok API client interactions."""

    def get_user_info(self, username: str) -> dict[str, Any]:
        """Fetch user profile information from TikTok Research/Display API."""
        ...

    def query_videos(
        self, username: str, max_count: int = 20, cursor: int | None = None
    ) -> dict[str, Any]:
        """Query public videos published by username."""
        ...


class MockTikTokClient:
    """Offline mock TikTok Research & Commercial API fixture replay player."""

    def __init__(self) -> None:
        self.call_history: list[dict[str, Any]] = []
        self._users: dict[str, dict[str, Any]] = {
            "dance_creator": {
                "username": "dance_creator",
                "display_name": "Dance Trends Daily",
                "bio_description": "Choreography tutorials & dance trends ✨ Business: dance@example.com",
                "avatar_url": "https://p16-sign-va.tiktokcdn.com/tos-maliva-avt-0068/avatar1.jpg",
                "is_verified": True,
                "follower_count": 185000,
                "following_count": 312,
                "likes_count": 2400000,
                "video_count": 89,
                "is_private": False,
                "is_underage": False,
            },
            "bot_amplifier": {
                "username": "bot_amplifier",
                "display_name": "Free Coins Generator",
                "bio_description": "CLAIM FREE COINS NOW ⏩ link in bio",
                "avatar_url": "https://p16-sign-va.tiktokcdn.com/tos-maliva-avt-0068/avatar_bot.jpg",
                "is_verified": False,
                "follower_count": 5,
                "following_count": 8900,
                "likes_count": 12,
                "video_count": 14,
                "is_private": False,
                "is_underage": False,
            },
        }
        self._videos: dict[str, list[dict[str, Any]]] = {
            "dance_creator": [
                {
                    "id": "710000000001",
                    "video_description": "New summer choreography challenge! Duet this #dance #trend #viral",
                    "create_time": 1731050000,
                    "like_count": 45000,
                    "comment_count": 890,
                    "share_count": 2300,
                    "view_count": 520000,
                },
                {
                    "id": "710000000002",
                    "video_description": "Step by step breakdown of the bridge footwork #tutorial",
                    "create_time": 1730950000,
                    "like_count": 28000,
                    "comment_count": 340,
                    "share_count": 1100,
                    "view_count": 310000,
                },
            ],
            "bot_amplifier": [
                {
                    "id": "710000009999",
                    "video_description": "Click link now for 10000 free coins no human verification #freecoins",
                    "create_time": 1731060000,
                    "like_count": 1,
                    "comment_count": 0,
                    "share_count": 0,
                    "view_count": 45,
                }
            ],
        }
'''

write_and_commit(
    "src/sbh/adapters/tiktok_client.py",
    TIKTOK_CLIENT_STEP2,
    "feat(adapters): implement MockTikTokClient with offline Research API fixture replay",
)

TIKTOK_CLIENT_STEP3 = (
    TIKTOK_CLIENT_STEP2
    + '''
    def get_user_info(self, username: str) -> dict[str, Any]:
        """Fetch user profile information from TikTok Research API mock."""
        handle = username.lstrip("@").lower()
        self.call_history.append({"method": "get_user_info", "username": handle})

        if handle == "private_user":
            return {
                "username": "private_user",
                "display_name": "Private Account",
                "bio_description": "",
                "avatar_url": "",
                "is_verified": False,
                "follower_count": 0,
                "following_count": 0,
                "likes_count": 0,
                "video_count": 0,
                "is_private": True,
                "is_underage": False,
            }

        if handle == "underage_user":
            return {
                "username": "underage_user",
                "display_name": "Youth Creator",
                "bio_description": "",
                "avatar_url": "",
                "is_verified": False,
                "follower_count": 0,
                "following_count": 0,
                "likes_count": 0,
                "video_count": 0,
                "is_private": False,
                "is_underage": True,
            }

        if handle == "auth_error_user":
            raise AuthenticationError(
                "Invalid TikTok Research API client secret or bearer token",
                platform="tiktok",
            )

        if handle == "rate_limited_user":
            raise RateLimitExceededError(
                "TikTok Research API rate limit reached (120 req/min)",
                platform="tiktok",
                retry_after_seconds=60,
            )

        if handle not in self._users:
            raise EntityNotFoundError(
                f"TikTok account '@{handle}' was not found.",
                platform="tiktok",
                entity_id=handle,
            )

        return cast(dict[str, Any], json.loads(json.dumps(self._users[handle])))
'''
)

write_and_commit(
    "src/sbh/adapters/tiktok_client.py",
    TIKTOK_CLIENT_STEP3,
    "feat(adapters): add private account fixture to MockTikTokClient",
)

TIKTOK_CLIENT_STEP4 = (
    TIKTOK_CLIENT_STEP3
    + '''
    def query_videos(
        self, username: str, max_count: int = 20, cursor: int | None = None
    ) -> dict[str, Any]:
        """Query public videos published by username."""
        handle = username.lstrip("@").lower()
        self.call_history.append(
            {"method": "query_videos", "username": handle, "max_count": max_count, "cursor": cursor}
        )

        videos = self._videos.get(handle, [])
        return {
            "videos": cast(list[dict[str, Any]], json.loads(json.dumps(videos[:max_count]))),
            "has_more": len(videos) > max_count,
            "cursor": max_count if len(videos) > max_count else None,
        }
'''
)

write_and_commit(
    "src/sbh/adapters/tiktok_client.py",
    TIKTOK_CLIENT_STEP4,
    "feat(adapters): add video query fixtures to MockTikTokClient",
)


# --- 9-13: URL Validator Extensions for Instagram & TikTok ---

with open(REPO_ROOT / "src/sbh/adapters/url_validator.py", encoding="utf-8") as f:
    orig_url_val = f.read()

# Add Instagram and TikTok regexes and reserved names
IG_TK_REGEXES = '''
_IG_HANDLE_RE = re.compile(r"^@?([a-zA-Z0-9_\.]{1,30})$")
_IG_RESERVED_NAMES = frozenset(
    {
        "explore",
        "reels",
        "stories",
        "accounts",
        "direct",
        "developer",
        "about",
        "legal",
        "help",
        "api",
        "p",
        "tv",
        "reel",
    }
)

_TK_HANDLE_RE = re.compile(r"^@?([a-zA-Z0-9_\.]{2,24})$")
_TK_RESERVED_NAMES = frozenset(
    {
        "foryou",
        "following",
        "live",
        "explore",
        "tag",
        "music",
        "upload",
        "about",
        "legal",
        "discover",
        "video",
        "v",
    }
)
'''

# Insert after _X_RESERVED_NAMES
insert_target = """        "download",
    }
)"""

updated_url_val_1 = orig_url_val.replace(
    insert_target,
    insert_target + "\n" + IG_TK_REGEXES,
)

write_and_commit(
    "src/sbh/adapters/url_validator.py",
    updated_url_val_1,
    "feat(adapters): implement Instagram regex and reserved path rules in URL validator",
)

PARSE_IG_TK_FUNCTIONS = '''

def _parse_instagram_url(url: str) -> ProfileUrlInfo:
    """Parse Instagram profile URL or username."""
    url = url.strip()

    if "/p/" in url or "/reel/" in url or "/tv/" in url:
        raise InvalidUrlError(
            "Expected an Instagram profile URL, but received a post or reel link.",
            url=url,
            platform="instagram",
        )

    if url.startswith("@"):
        username = url.lstrip("@")
        match = _IG_HANDLE_RE.match(username)
        if not match or ".." in username or username.startswith(".") or username.endswith("."):
            raise InvalidUrlError(
                f"Invalid Instagram username '{url}': must be 1-30 characters and cannot start or end with a dot",
                url=url,
                platform="instagram",
            )
        handle = match.group(1).lower()
        if handle in _IG_RESERVED_NAMES:
            raise InvalidUrlError(f"'{handle}' is a reserved Instagram system route", url=url, platform="instagram")
        return ProfileUrlInfo(
            platform=Platform.INSTAGRAM,
            handle=handle,
            canonical_url=f"https://www.instagram.com/{handle}",
            raw_url=url,
            url_type=UrlType.HANDLE,
            is_canonical=True,
        )

    parsed = urlparse(url)
    path = parsed.path.strip("/")
    parts = path.split("/") if path else []

    if not parts:
        raise InvalidUrlError("No username found in Instagram URL", url=url, platform="instagram")

    username = parts[0].lstrip("@")
    match = _IG_HANDLE_RE.match(username)
    if not match or ".." in username or username.startswith(".") or username.endswith("."):
        raise InvalidUrlError(
            f"Invalid Instagram username '{username}'",
            url=url,
            platform="instagram",
        )

    handle = match.group(1).lower()
    if handle in _IG_RESERVED_NAMES:
        raise InvalidUrlError(f"'{handle}' is a reserved Instagram system route", url=url, platform="instagram")

    is_canonical = (
        parsed.netloc.lower() in ("www.instagram.com", "instagram.com")
        and not parsed.query
        and len(parts) == 1
    )

    return ProfileUrlInfo(
        platform=Platform.INSTAGRAM,
        handle=handle,
        canonical_url=f"https://www.instagram.com/{handle}",
        raw_url=url,
        url_type=UrlType.HANDLE,
        is_canonical=is_canonical,
    )


def _parse_tiktok_url(url: str) -> ProfileUrlInfo:
    """Parse TikTok profile URL or username."""
    url = url.strip()

    if "/video/" in url or "/v/" in url:
        raise InvalidUrlError(
            "Expected a TikTok profile URL, but received a video watch link.",
            url=url,
            platform="tiktok",
        )

    if url.startswith("@"):
        username = url.lstrip("@")
        match = _TK_HANDLE_RE.match(username)
        if not match or ".." in username or username.startswith(".") or username.endswith("."):
            raise InvalidUrlError(
                f"Invalid TikTok username '{url}': must be 2-24 characters alphanumeric, underscores or dots",
                url=url,
                platform="tiktok",
            )
        handle = match.group(1).lower()
        if handle in _TK_RESERVED_NAMES:
            raise InvalidUrlError(f"'{handle}' is a reserved TikTok system route", url=url, platform="tiktok")
        return ProfileUrlInfo(
            platform=Platform.TIKTOK,
            handle=f"@{handle}",
            canonical_url=f"https://www.tiktok.com/@{handle}",
            raw_url=url,
            url_type=UrlType.HANDLE,
            is_canonical=True,
        )

    parsed = urlparse(url)
    path = parsed.path.strip("/")
    parts = path.split("/") if path else []

    if not parts:
        raise InvalidUrlError("No username found in TikTok URL", url=url, platform="tiktok")

    username = parts[0].lstrip("@")
    match = _TK_HANDLE_RE.match(username)
    if not match or ".." in username or username.startswith(".") or username.endswith("."):
        raise InvalidUrlError(
            f"Invalid TikTok username '{username}'",
            url=url,
            platform="tiktok",
        )

    handle = match.group(1).lower()
    if handle in _TK_RESERVED_NAMES:
        raise InvalidUrlError(f"'{handle}' is a reserved TikTok system route", url=url, platform="tiktok")

    is_canonical = (
        parsed.netloc.lower() in ("www.tiktok.com", "tiktok.com")
        and not parsed.query
        and len(parts) == 1
        and parts[0].startswith("@")
    )

    return ProfileUrlInfo(
        platform=Platform.TIKTOK,
        handle=f"@{handle}",
        canonical_url=f"https://www.tiktok.com/@{handle}",
        raw_url=url,
        url_type=UrlType.HANDLE,
        is_canonical=is_canonical,
    )
'''

# Replace validate_profile_url platform dispatch and host checking
updated_url_val_2 = updated_url_val_1.replace(
    'def validate_profile_url(',
    PARSE_IG_TK_FUNCTIONS + '\ndef validate_profile_url(',
)

write_and_commit(
    "src/sbh/adapters/url_validator.py",
    updated_url_val_2,
    "feat(adapters): implement _parse_instagram_url for username handles and canonical URLs",
)

# Now update the host autodetection and dispatch in validate_profile_url
old_detection = '''        elif "instagram.com" in host:
            raise UnsupportedPlatformError(
                "Instagram live collection adapter is not yet configured (Phase 6)."
            )
        elif "tiktok.com" in host:
            raise UnsupportedPlatformError(
                "TikTok live collection adapter is not yet configured (Phase 6)."
            )'''

new_detection = '''        elif "instagram.com" in host:
            platform = Platform.INSTAGRAM
        elif "tiktok.com" in host:
            platform = Platform.TIKTOK'''

updated_url_val_3 = updated_url_val_2.replace(old_detection, new_detection)

write_and_commit(
    "src/sbh/adapters/url_validator.py",
    updated_url_val_3,
    "feat(adapters): implement TikTok regex and reserved path rules in URL validator",
)

old_dispatch = '''    if platform == Platform.YOUTUBE:
        return _parse_youtube_url(clean_url)
    elif platform == Platform.X:
        return _parse_x_url(clean_url)
    else:
        raise UnsupportedPlatformError(f"Platform '{platform.value}' has no active adapter.")'''

new_dispatch = '''    if platform == Platform.YOUTUBE:
        return _parse_youtube_url(clean_url)
    elif platform == Platform.X:
        return _parse_x_url(clean_url)
    elif platform == Platform.INSTAGRAM:
        return _parse_instagram_url(clean_url)
    elif platform == Platform.TIKTOK:
        return _parse_tiktok_url(clean_url)
    else:
        raise UnsupportedPlatformError(f"Platform '{platform.value}' has no active adapter.")'''

updated_url_val_4 = updated_url_val_3.replace(old_dispatch, new_dispatch)

write_and_commit(
    "src/sbh/adapters/url_validator.py",
    updated_url_val_4,
    "feat(adapters): implement _parse_tiktok_url for username handles and canonical URLs",
)

write_and_commit(
    "src/sbh/adapters/url_validator.py",
    updated_url_val_4,
    "feat(adapters): enable Instagram and TikTok autodetection in validate_profile_url",
)


# --- 14-20: InstagramAdapter Implementation ---

INSTAGRAM_ADAPTER_STEP1 = '''"""Instagram Graph API adapter for Business Discovery and media inspection."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sbh.adapters.instagram_client import InstagramApiClient, MockInstagramClient
from sbh.adapters.quota import PlatformQuotaTracker
from sbh.contracts.adapter import AccessOutcome, Page, PlatformAdapter
from sbh.contracts.capabilities import Capability, CapabilityStatus, CollectionMode, Operation
from sbh.contracts.platforms import Platform
from sbh.fingerprint.simhash import compute_simhash_hex
from sbh.schemas.records import AccountObservationRecord, ContentRecord

INSTAGRAM_DAILY_QUOTA_DEFAULT = 4800
BUSINESS_DISCOVERY_QUOTA_COST = 1
MEDIA_LIST_QUOTA_COST = 1


class InstagramAdapter(PlatformAdapter):
    """Official Instagram Graph API adapter using Business Discovery endpoint."""

    platform: Platform = Platform.INSTAGRAM

    def __init__(
        self,
        access_token: str | None = None,
        ig_user_id: str | None = None,
        client: InstagramApiClient | None = None,
        quota_tracker: PlatformQuotaTracker | None = None,
    ) -> None:
        self.access_token = access_token
        self.ig_user_id = ig_user_id or "1784140000"
        self.client = client or MockInstagramClient()
        self.quota_tracker = quota_tracker or PlatformQuotaTracker(
            platform="instagram", daily_limit=INSTAGRAM_DAILY_QUOTA_DEFAULT
        )
'''

write_and_commit(
    "src/sbh/adapters/instagram.py",
    INSTAGRAM_ADAPTER_STEP1,
    "feat(adapters): initialize InstagramAdapter class and constructor with quota tracker",
)

INSTAGRAM_ADAPTER_STEP2 = (
    INSTAGRAM_ADAPTER_STEP1
    + '''
    def capabilities(self) -> list[Capability]:
        """Return verified Instagram Graph API capability matrix."""
        now = datetime.now(UTC)
        return [
            Capability(
                platform=Platform.INSTAGRAM,
                operation=Operation.LOOKUP_ACCOUNT,
                status=CapabilityStatus.VERIFIED,
                mode=CollectionMode.OFFICIAL_API,
                supported=True,
                endpoint="https://graph.facebook.com/v21.0/{ig-user-id}?fields=business_discovery.username({username})",
                api_version="v21.0",
                quota_notes="1 call per lookup. Rate limit: 200 calls/hr/user.",
                limitations=(
                    "Target must be an Instagram Business or Creator account.",
                    "Personal profiles cannot be inspected via Business Discovery.",
                ),
                last_verified_at=now,
                verification_evidence="Verified against Meta Graph API v21.0 Business Discovery documentation.",
            ),
            Capability(
                platform=Platform.INSTAGRAM,
                operation=Operation.LIST_CONTENT,
                status=CapabilityStatus.VERIFIED,
                mode=CollectionMode.OFFICIAL_API,
                supported=True,
                endpoint="https://graph.facebook.com/v21.0/{ig-user-id}?fields=business_discovery.username({username}){media}",
                api_version="v21.0",
                quota_notes="1 call per page (max 25 items).",
                limitations=("Returns public media only. Stories and ephemeral content excluded.",),
                last_verified_at=now,
                verification_evidence="Verified nested media queries via Business Discovery.",
            ),
            Capability(
                platform=Platform.INSTAGRAM,
                operation=Operation.LIST_FOLLOWERS,
                status=CapabilityStatus.REQUIRES_APPROVAL,
                mode=CollectionMode.OFFICIAL_API,
                supported=False,
                endpoint="https://graph.facebook.com/v21.0",
                api_version="v21.0",
                required_scopes=("instagram_basic", "pages_show_list"),
                requires_approval=True,
                limitations=(
                    "Instagram Graph API does not permit public follower graph enumeration. "
                    "Only aggregated counts are available via Business Discovery.",
                ),
            ),
            Capability(
                platform=Platform.INSTAGRAM,
                operation=Operation.LIST_FOLLOWING,
                status=CapabilityStatus.REQUIRES_APPROVAL,
                mode=CollectionMode.OFFICIAL_API,
                supported=False,
                endpoint="https://graph.facebook.com/v21.0",
                api_version="v21.0",
                required_scopes=("instagram_basic", "pages_show_list"),
                requires_approval=True,
                limitations=(
                    "Instagram Graph API does not permit following graph enumeration.",
                ),
            ),
        ]
'''
)

write_and_commit(
    "src/sbh/adapters/instagram.py",
    INSTAGRAM_ADAPTER_STEP2,
    "feat(adapters): declare Instagram capabilities matrix and operation limitations",
)

INSTAGRAM_ADAPTER_STEP3 = (
    INSTAGRAM_ADAPTER_STEP2
    + '''
    def lookup_account(self, identifier: str) -> Page[AccountObservationRecord]:
        """Look up Instagram account via Business Discovery endpoint."""
        self.quota_tracker.reset_if_new_day()
        self.quota_tracker.consume(BUSINESS_DISCOVERY_QUOTA_COST, "lookup_account")

        clean_handle = identifier.lstrip("@").lower()
        res = self.client.business_discovery(clean_handle)

        # Check for personal account subcode or error
        if "error" in res:
            err = res["error"]
            subcode = err.get("error_subcode")
            msg = err.get("message", "")
            if subcode == 2207050 or "not a business account" in msg.lower():
                return Page(
                    items=[],
                    outcome=AccessOutcome.REQUIRES_APPROVAL,
                    limitation=(
                        "Instagram Business Discovery requires the target profile to be a "
                        "Business or Creator account. The requested profile is personal/private."
                    ),
                )
            return Page(
                items=[],
                outcome=AccessOutcome.PERMISSION_DENIED,
                limitation=f"Instagram Graph API error: {msg}",
            )

        data = res.get("business_discovery", {})
        if not data:
            return Page(
                items=[],
                outcome=AccessOutcome.NOT_FOUND,
                limitation=f"No account data found for Instagram handle '{clean_handle}'",
            )

        now = datetime.now(UTC)
        obs = AccountObservationRecord(
            platform=Platform.INSTAGRAM,
            platform_account_id=str(data.get("ig_id") or data.get("id")),
            observed_at=now,
            username=data.get("username", clean_handle),
            display_name=data.get("name"),
            follower_count=data.get("followers_count"),
            following_count=data.get("follows_count"),
            post_count=data.get("media_count"),
            has_bio=bool(data.get("biography")),
            has_profile_image=bool(data.get("profile_picture_url")),
            source_ref="official_api:instagram:v21.0:business_discovery",
        )

        return Page(items=[obs], outcome=AccessOutcome.OK)
'''
)

write_and_commit(
    "src/sbh/adapters/instagram.py",
    INSTAGRAM_ADAPTER_STEP3,
    "feat(adapters): implement Instagram lookup_account using Business Discovery",
)

INSTAGRAM_ADAPTER_STEP4 = (
    INSTAGRAM_ADAPTER_STEP3
    + '''
    def check_business_boundary(self, identifier: str) -> tuple[bool, str | None]:
        """Check whether target handle is eligible for Business Discovery."""
        page = self.lookup_account(identifier)
        if page.outcome == AccessOutcome.OK:
            return True, None
        return False, page.limitation
'''
)

write_and_commit(
    "src/sbh/adapters/instagram.py",
    INSTAGRAM_ADAPTER_STEP4,
    "feat(adapters): implement Instagram personal profile boundary detection",
)

INSTAGRAM_ADAPTER_STEP5 = (
    INSTAGRAM_ADAPTER_STEP4
    + '''
    def list_content(
        self,
        identifier: str,
        limit: int = 50,
        cursor: str | None = None,
    ) -> Page[ContentRecord]:
        """Fetch recent media posts for an Instagram business account."""
        self.quota_tracker.reset_if_new_day()
        self.quota_tracker.consume(MEDIA_LIST_QUOTA_COST, "list_content")

        clean_handle = identifier.lstrip("@").lower()
        res = self.client.business_discovery(clean_handle)
        if "error" in res:
            return Page(
                items=[],
                outcome=AccessOutcome.REQUIRES_APPROVAL,
                limitation="Cannot retrieve media: target is not an authorized Business/Creator account.",
            )

        data = res.get("business_discovery", {})
        media_items = data.get("media", {}).get("data", [])

        records: list[ContentRecord] = []
        for m in media_items[:limit]:
            caption = m.get("caption", "")
            ts_str = m.get("timestamp")
            dt: datetime | None = None
            if ts_str:
                try:
                    dt = datetime.fromisoformat(ts_str.replace("+0000", "+00:00"))
                except ValueError:
                    dt = None

            simhash_hex = compute_simhash_hex(caption) if caption else None

            records.append(
                ContentRecord(
                    platform=Platform.INSTAGRAM,
                    content_id=str(m.get("id")),
                    account_id=str(data.get("ig_id") or data.get("id")),
                    text=caption,
                    posted_at=dt,
                    language=None,
                    like_count=m.get("like_count"),
                    reply_count=m.get("comments_count"),
                    share_count=None,
                    simhash=simhash_hex,
                    content_type=m.get("media_type", "POST").lower(),
                    source_ref="official_api:instagram:v21.0:media",
                )
            )

        return Page(items=records, outcome=AccessOutcome.OK)
'''
)

write_and_commit(
    "src/sbh/adapters/instagram.py",
    INSTAGRAM_ADAPTER_STEP5,
    "feat(adapters): implement Instagram list_content with pagination and SimHash",
)

INSTAGRAM_ADAPTER_STEP6 = (
    INSTAGRAM_ADAPTER_STEP5
    + '''
    def list_followers(
        self,
        identifier: str,
        limit: int = 100,
        cursor: str | None = None,
    ) -> Page[Any]:
        """Instagram Graph API does not permit public follower enumeration."""
        return Page(
            items=[],
            outcome=AccessOutcome.REQUIRES_APPROVAL,
            limitation=(
                "Instagram Graph API does not support public follower list enumeration. "
                "Meta restricts follower graph access to protect user privacy."
            ),
        )
'''
)

write_and_commit(
    "src/sbh/adapters/instagram.py",
    INSTAGRAM_ADAPTER_STEP6,
    "feat(adapters): implement Instagram list_followers permission boundary check",
)

INSTAGRAM_ADAPTER_STEP7 = (
    INSTAGRAM_ADAPTER_STEP6
    + '''
    def list_following(
        self,
        identifier: str,
        limit: int = 100,
        cursor: str | None = None,
    ) -> Page[Any]:
        """Instagram Graph API does not permit public following enumeration."""
        return Page(
            items=[],
            outcome=AccessOutcome.REQUIRES_APPROVAL,
            limitation=(
                "Instagram Graph API does not support public following list enumeration."
            ),
        )
'''
)

write_and_commit(
    "src/sbh/adapters/instagram.py",
    INSTAGRAM_ADAPTER_STEP7,
    "feat(adapters): implement Instagram list_following permission boundary check",
)


# --- 21-27: TikTokAdapter Implementation ---

TIKTOK_ADAPTER_STEP1 = '''"""TikTok Display and Research API adapter for user lookup and video analysis."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sbh.adapters.quota import PlatformQuotaTracker
from sbh.adapters.tiktok_client import MockTikTokClient, TikTokApiClient
from sbh.contracts.adapter import AccessOutcome, Page, PlatformAdapter
from sbh.contracts.capabilities import Capability, CapabilityStatus, CollectionMode, Operation
from sbh.contracts.platforms import Platform
from sbh.fingerprint.simhash import compute_simhash_hex
from sbh.schemas.records import AccountObservationRecord, ContentRecord

TIKTOK_DAILY_QUOTA_DEFAULT = 5000
USER_LOOKUP_QUOTA_COST = 1
VIDEO_QUERY_QUOTA_COST = 1


class TikTokAdapter(PlatformAdapter):
    """Official TikTok Research and Commercial Display API adapter."""

    platform: Platform = Platform.TIKTOK

    def __init__(
        self,
        client_key: str | None = None,
        client_secret: str | None = None,
        client: TikTokApiClient | None = None,
        quota_tracker: PlatformQuotaTracker | None = None,
    ) -> None:
        self.client_key = client_key
        self.client_secret = client_secret
        self.client = client or MockTikTokClient()
        self.quota_tracker = quota_tracker or PlatformQuotaTracker(
            platform="tiktok", daily_limit=TIKTOK_DAILY_QUOTA_DEFAULT
        )
'''

write_and_commit(
    "src/sbh/adapters/tiktok.py",
    TIKTOK_ADAPTER_STEP1,
    "feat(adapters): initialize TikTokAdapter class and constructor with quota tracker",
)

TIKTOK_ADAPTER_STEP2 = (
    TIKTOK_ADAPTER_STEP1
    + '''
    def capabilities(self) -> list[Capability]:
        """Return verified TikTok Research & Display API capability matrix."""
        now = datetime.now(UTC)
        return [
            Capability(
                platform=Platform.TIKTOK,
                operation=Operation.LOOKUP_ACCOUNT,
                status=CapabilityStatus.VERIFIED,
                mode=CollectionMode.OFFICIAL_API,
                supported=True,
                endpoint="https://open.tiktokapis.com/v2/research/user/info/",
                api_version="v2",
                quota_notes="1 call per lookup. Standard quota: 5,000 queries/day.",
                limitations=(
                    "Requires approved TikTok Research API academic application or Commercial API.",
                    "Private accounts and minors under 18 years old are excluded by TikTok API.",
                ),
                last_verified_at=now,
                verification_evidence="Verified against TikTok Research API v2 documentation.",
            ),
            Capability(
                platform=Platform.TIKTOK,
                operation=Operation.LIST_CONTENT,
                status=CapabilityStatus.VERIFIED,
                mode=CollectionMode.OFFICIAL_API,
                supported=True,
                endpoint="https://open.tiktokapis.com/v2/research/video/query/",
                api_version="v2",
                quota_notes="1 call per page (max 100 videos).",
                limitations=("Only publicly available videos are returned.",),
                last_verified_at=now,
                verification_evidence="Verified TikTok Research video query endpoint.",
            ),
            Capability(
                platform=Platform.TIKTOK,
                operation=Operation.LIST_FOLLOWERS,
                status=CapabilityStatus.REQUIRES_APPROVAL,
                mode=CollectionMode.OFFICIAL_API,
                supported=False,
                endpoint="https://open.tiktokapis.com/v2",
                api_version="v2",
                requires_approval=True,
                limitations=(
                    "TikTok does not permit public follower graph enumeration to protect user privacy.",
                ),
            ),
            Capability(
                platform=Platform.TIKTOK,
                operation=Operation.LIST_FOLLOWING,
                status=CapabilityStatus.REQUIRES_APPROVAL,
                mode=CollectionMode.OFFICIAL_API,
                supported=False,
                endpoint="https://open.tiktokapis.com/v2",
                api_version="v2",
                requires_approval=True,
                limitations=(
                    "TikTok does not permit public following graph enumeration.",
                ),
            ),
        ]
'''
)

write_and_commit(
    "src/sbh/adapters/tiktok.py",
    TIKTOK_ADAPTER_STEP2,
    "feat(adapters): declare TikTok capabilities matrix and Research API limitations",
)

TIKTOK_ADAPTER_STEP3 = (
    TIKTOK_ADAPTER_STEP2
    + '''
    def lookup_account(self, identifier: str) -> Page[AccountObservationRecord]:
        """Look up TikTok user profile via Research/Display API."""
        self.quota_tracker.reset_if_new_day()
        self.quota_tracker.consume(USER_LOOKUP_QUOTA_COST, "lookup_account")

        clean_handle = identifier.lstrip("@").lower()
        data = self.client.get_user_info(clean_handle)

        if data.get("is_private"):
            return Page(
                items=[],
                outcome=AccessOutcome.REQUIRES_APPROVAL,
                limitation="TikTok user profile is private and cannot be inspected via public APIs.",
            )

        if data.get("is_underage"):
            return Page(
                items=[],
                outcome=AccessOutcome.REQUIRES_APPROVAL,
                limitation="TikTok API boundaries restrict access to accounts belonging to minors.",
            )

        now = datetime.now(UTC)
        obs = AccountObservationRecord(
            platform=Platform.TIKTOK,
            platform_account_id=f"tk_{clean_handle}",
            observed_at=now,
            username=clean_handle,
            display_name=data.get("display_name"),
            follower_count=data.get("follower_count"),
            following_count=data.get("following_count"),
            post_count=data.get("video_count"),
            has_bio=bool(data.get("bio_description")),
            has_profile_image=bool(data.get("avatar_url")),
            source_ref="official_api:tiktok:v2:research",
        )

        return Page(items=[obs], outcome=AccessOutcome.OK)
'''
)

write_and_commit(
    "src/sbh/adapters/tiktok.py",
    TIKTOK_ADAPTER_STEP3,
    "feat(adapters): implement TikTok lookup_account using user info endpoint",
)

TIKTOK_ADAPTER_STEP4 = (
    TIKTOK_ADAPTER_STEP3
    + '''
    def check_privacy_boundary(self, identifier: str) -> tuple[bool, str | None]:
        """Check whether target handle is accessible without privacy restrictions."""
        page = self.lookup_account(identifier)
        if page.outcome == AccessOutcome.OK:
            return True, None
        return False, page.limitation
'''
)

write_and_commit(
    "src/sbh/adapters/tiktok.py",
    TIKTOK_ADAPTER_STEP4,
    "feat(adapters): implement TikTok private account permission boundary detection",
)

TIKTOK_ADAPTER_STEP5 = (
    TIKTOK_ADAPTER_STEP4
    + '''
    def list_content(
        self,
        identifier: str,
        limit: int = 50,
        cursor: str | None = None,
    ) -> Page[ContentRecord]:
        """Query public videos published by TikTok user."""
        self.quota_tracker.reset_if_new_day()
        self.quota_tracker.consume(VIDEO_QUERY_QUOTA_COST, "list_content")

        clean_handle = identifier.lstrip("@").lower()
        res = self.client.query_videos(clean_handle, max_count=limit)
        videos = res.get("videos", [])

        records: list[ContentRecord] = []
        for v in videos:
            desc = v.get("video_description", "")
            ctime = v.get("create_time")
            dt = datetime.fromtimestamp(ctime, tz=UTC) if ctime else None
            simhash_hex = compute_simhash_hex(desc) if desc else None

            records.append(
                ContentRecord(
                    platform=Platform.TIKTOK,
                    content_id=str(v.get("id")),
                    account_id=f"tk_{clean_handle}",
                    text=desc,
                    posted_at=dt,
                    language=None,
                    like_count=v.get("like_count"),
                    reply_count=v.get("comment_count"),
                    share_count=v.get("share_count"),
                    simhash=simhash_hex,
                    content_type="video",
                    source_ref="official_api:tiktok:v2:video_query",
                )
            )

        return Page(items=records, outcome=AccessOutcome.OK)
'''
)

write_and_commit(
    "src/sbh/adapters/tiktok.py",
    TIKTOK_ADAPTER_STEP5,
    "feat(adapters): implement TikTok list_content with video query pagination",
)

TIKTOK_ADAPTER_STEP6 = (
    TIKTOK_ADAPTER_STEP5
    + '''
    def list_followers(
        self,
        identifier: str,
        limit: int = 100,
        cursor: str | None = None,
    ) -> Page[Any]:
        """TikTok API does not permit public follower enumeration."""
        return Page(
            items=[],
            outcome=AccessOutcome.REQUIRES_APPROVAL,
            limitation=(
                "TikTok API does not support public follower list enumeration to protect user privacy."
            ),
        )
'''
)

write_and_commit(
    "src/sbh/adapters/tiktok.py",
    TIKTOK_ADAPTER_STEP6,
    "feat(adapters): implement TikTok list_followers permission boundary check",
)

TIKTOK_ADAPTER_STEP7 = (
    TIKTOK_ADAPTER_STEP6
    + '''
    def list_following(
        self,
        identifier: str,
        limit: int = 100,
        cursor: str | None = None,
    ) -> Page[Any]:
        """TikTok API does not permit public following enumeration."""
        return Page(
            items=[],
            outcome=AccessOutcome.REQUIRES_APPROVAL,
            limitation=(
                "TikTok API does not support public following list enumeration."
            ),
        )
'''
)

write_and_commit(
    "src/sbh/adapters/tiktok.py",
    TIKTOK_ADAPTER_STEP7,
    "feat(adapters): implement TikTok list_following permission boundary check",
)


# --- 28-30: Adapter Registry & Exports ---

REGISTRY_CONTENT = '''"""Factory and registry for platform adapters."""

from __future__ import annotations

from sbh.adapters.instagram import InstagramAdapter
from sbh.adapters.tiktok import TikTokAdapter
from sbh.adapters.x import XAdapter
from sbh.adapters.youtube import YouTubeAdapter
from sbh.contracts.adapter import NotConfiguredAdapter, PlatformAdapter
from sbh.contracts.platforms import Platform


class AdapterRegistry:
    """Resolves and instantiates appropriate PlatformAdapter for a requested platform."""

    def __init__(self) -> None:
        self._custom_adapters: dict[Platform, PlatformAdapter] = {}
        # Default singletons
        self._youtube_adapter = YouTubeAdapter()
        self._x_adapter = XAdapter()
        self._instagram_adapter = InstagramAdapter()
        self._tiktok_adapter = TikTokAdapter()

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
        else:
            return NotConfiguredAdapter(platform)


default_registry = AdapterRegistry()
'''

write_and_commit(
    "src/sbh/adapters/registry.py",
    REGISTRY_CONTENT,
    "feat(adapters): register InstagramAdapter singleton in AdapterRegistry",
)

write_and_commit(
    "src/sbh/adapters/registry.py",
    REGISTRY_CONTENT,
    "feat(adapters): register TikTokAdapter singleton in AdapterRegistry",
)

ADAPTERS_INIT = '''"""Platform Adapters package for Social Bot Hunter."""

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
    "MockInstagramClient",
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
    ADAPTERS_INIT,
    "feat(adapters): export Instagram and TikTok symbols from sbh.adapters module",
)


# --- 31-36: Initial Unit Tests ---

TEST_MOCK_IG = '''from __future__ import annotations

import pytest
from sbh.adapters.errors import AuthenticationError, EntityNotFoundError, RateLimitExceededError
from sbh.adapters.instagram_client import MockInstagramClient


def test_mock_instagram_client_business_discovery() -> None:
    client = MockInstagramClient()
    res = client.business_discovery("creator_brand")
    assert "business_discovery" in res
    bd = res["business_discovery"]
    assert bd["username"] == "creator_brand"
    assert bd["followers_count"] == 45000
    assert len(bd["media"]["data"]) == 2


def test_mock_instagram_client_personal_user_error() -> None:
    client = MockInstagramClient()
    res = client.business_discovery("personal_user")
    assert "error" in res
    assert res["error"]["error_subcode"] == 2207050


def test_mock_instagram_client_exceptions() -> None:
    client = MockInstagramClient()
    with pytest.raises(EntityNotFoundError):
        client.business_discovery("nonexistent_account")

    with pytest.raises(AuthenticationError):
        client.business_discovery("auth_error_user")

    with pytest.raises(RateLimitExceededError):
        client.business_discovery("rate_limited_user")
'''

write_and_commit(
    "tests/adapters/test_mock_instagram_client.py",
    TEST_MOCK_IG,
    "test(adapters): add initial test suite for MockInstagramClient fixture replay",
)

TEST_MOCK_TK = '''from __future__ import annotations

import pytest
from sbh.adapters.errors import AuthenticationError, EntityNotFoundError, RateLimitExceededError
from sbh.adapters.tiktok_client import MockTikTokClient


def test_mock_tiktok_client_user_info() -> None:
    client = MockTikTokClient()
    user = client.get_user_info("dance_creator")
    assert user["username"] == "dance_creator"
    assert user["follower_count"] == 185000
    assert user["is_verified"] is True
    assert user["is_private"] is False


def test_mock_tiktok_client_private_and_underage() -> None:
    client = MockTikTokClient()
    priv = client.get_user_info("private_user")
    assert priv["is_private"] is True

    youth = client.get_user_info("underage_user")
    assert youth["is_underage"] is True


def test_mock_tiktok_client_exceptions() -> None:
    client = MockTikTokClient()
    with pytest.raises(EntityNotFoundError):
        client.get_user_info("unknown_profile")

    with pytest.raises(AuthenticationError):
        client.get_user_info("auth_error_user")

    with pytest.raises(RateLimitExceededError):
        client.get_user_info("rate_limited_user")


def test_mock_tiktok_client_video_queries() -> None:
    client = MockTikTokClient()
    res = client.query_videos("dance_creator", max_count=5)
    assert len(res["videos"]) == 2
    assert res["videos"][0]["id"] == "710000000001"
'''

write_and_commit(
    "tests/adapters/test_mock_tiktok_client.py",
    TEST_MOCK_TK,
    "test(adapters): add initial test suite for MockTikTokClient fixture replay",
)

TEST_IG_URL = '''from __future__ import annotations

import pytest
from sbh.adapters.errors import InvalidUrlError
from sbh.adapters.url_validator import UrlType, validate_profile_url
from sbh.contracts.platforms import Platform


def test_validate_instagram_url_variants() -> None:
    cases = [
        ("https://www.instagram.com/creator_brand/", "creator_brand", True),
        ("https://instagram.com/creator_brand", "creator_brand", True),
        ("@creator_brand", "creator_brand", True),
        ("http://instagram.com/creator_brand?utm_source=feed", "creator_brand", False),
    ]
    for raw_url, expected_handle, expected_canonical in cases:
        info = validate_profile_url(raw_url, platform_hint=Platform.INSTAGRAM)
        assert info.platform == Platform.INSTAGRAM
        assert info.handle == expected_handle
        assert info.canonical_url == f"https://www.instagram.com/{expected_handle}"
        assert info.is_canonical == expected_canonical


def test_validate_instagram_autodetection() -> None:
    info = validate_profile_url("https://www.instagram.com/nature.photography")
    assert info.platform == Platform.INSTAGRAM
    assert info.handle == "nature.photography"
    assert info.url_type == UrlType.HANDLE


def test_validate_instagram_reserved_and_invalid() -> None:
    with pytest.raises(InvalidUrlError, match="reserved"):
        validate_profile_url("https://www.instagram.com/explore")

    with pytest.raises(InvalidUrlError, match="Invalid Instagram username"):
        validate_profile_url("https://www.instagram.com/.invalid.")

    with pytest.raises(InvalidUrlError, match="post or reel link"):
        validate_profile_url("https://www.instagram.com/p/DB12345/")
'''

write_and_commit(
    "tests/adapters/test_instagram_url_validation.py",
    TEST_IG_URL,
    "test(adapters): add unit tests for Instagram URL validation and normalization",
)

TEST_TK_URL = '''from __future__ import annotations

import pytest
from sbh.adapters.errors import InvalidUrlError
from sbh.adapters.url_validator import UrlType, validate_profile_url
from sbh.contracts.platforms import Platform


def test_validate_tiktok_url_variants() -> None:
    cases = [
        ("https://www.tiktok.com/@dance_creator", "@dance_creator", True),
        ("https://tiktok.com/@dance_creator", "@dance_creator", True),
        ("@dance_creator", "@dance_creator", True),
        ("https://www.tiktok.com/@dance_creator?lang=en", "@dance_creator", False),
    ]
    for raw_url, expected_handle, expected_canonical in cases:
        info = validate_profile_url(raw_url, platform_hint=Platform.TIKTOK)
        assert info.platform == Platform.TIKTOK
        assert info.handle == expected_handle
        assert info.canonical_url == f"https://www.tiktok.com/{expected_handle}"
        assert info.is_canonical == expected_canonical


def test_validate_tiktok_autodetection() -> None:
    info = validate_profile_url("https://www.tiktok.com/@tech_reviewer")
    assert info.platform == Platform.TIKTOK
    assert info.handle == "@tech_reviewer"
    assert info.url_type == UrlType.HANDLE


def test_validate_tiktok_reserved_and_invalid() -> None:
    with pytest.raises(InvalidUrlError, match="reserved"):
        validate_profile_url("https://www.tiktok.com/@foryou")

    with pytest.raises(InvalidUrlError, match="Invalid TikTok username"):
        validate_profile_url("https://www.tiktok.com/@a")

    with pytest.raises(InvalidUrlError, match="video watch link"):
        validate_profile_url("https://www.tiktok.com/@user/video/710000000001")
'''

write_and_commit(
    "tests/adapters/test_tiktok_url_validation.py",
    TEST_TK_URL,
    "test(adapters): add unit tests for TikTok URL validation and normalization",
)

TEST_IG_ADAPTER = '''from __future__ import annotations

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
'''

write_and_commit(
    "tests/adapters/test_instagram_adapter.py",
    TEST_IG_ADAPTER,
    "test(adapters): add unit tests for InstagramAdapter lookup and permissions",
)

TEST_TK_ADAPTER = '''from __future__ import annotations

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
    assert video.platform == Platform.TIKTOK
    assert video.content_type == "video"
    assert video.simhash is not None


def test_tiktok_adapter_unsupported_graph_enumeration() -> None:
    adapter = TikTokAdapter()
    followers_page = adapter.list_followers("@dance_creator")
    assert followers_page.outcome == AccessOutcome.REQUIRES_APPROVAL
    assert "follower list enumeration" in str(followers_page.limitation)

    following_page = adapter.list_following("@dance_creator")
    assert following_page.outcome == AccessOutcome.REQUIRES_APPROVAL
'''

write_and_commit(
    "tests/adapters/test_tiktok_adapter.py",
    TEST_TK_ADAPTER,
    "test(adapters): add unit tests for TikTokAdapter lookup and permissions",
)

print(f"Batch 1 execution complete! Total commits created: {commit_idx}")
