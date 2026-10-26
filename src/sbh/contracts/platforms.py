"""Platform identifiers. Each platform is its own identity namespace."""

from __future__ import annotations

from enum import StrEnum


class Platform(StrEnum):
    INSTAGRAM = "instagram"
    X = "x"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    LINKEDIN = "linkedin"


PLATFORM_VALUES: tuple[str, ...] = tuple(p.value for p in Platform)
