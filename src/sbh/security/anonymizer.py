"""Deterministic pseudonymization and field sanitization for social data."""

from __future__ import annotations

import hashlib
import hmac
from typing import Any

DEFAULT_SALT = "sbh_offline_privacy_salt_v1"


def pseudonymize_identifier(raw_id: str, salt: str = DEFAULT_SALT) -> str:
    """Create deterministic, irreversible pseudonymized ID using HMAC-SHA256."""
    h = hmac.new(salt.encode("utf-8"), raw_id.encode("utf-8"), hashlib.sha256)
    return f"anon_{h.hexdigest()[:16]}"


def mask_ip_address(ip: str) -> str:
    """Zero out host bits for IPv4/IPv6 addresses."""
    if "." in ip:
        parts = ip.split(".")
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.0.0"
    return "0.0.0.0"


def mask_phone_number(phone: str) -> str:
    """Mask phone number keeping only final 2 digits."""
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) >= 4:
        return f"+***-***-**{digits[-2:]}"
    return "+***-***"


def sanitize_profile_attributes(attrs: dict[str, Any]) -> dict[str, Any]:
    """Strip or redact sensitive PII fields from social profile dictionary."""
    sanitized = dict(attrs)
    sensitive_keys = {"email", "phone", "ip_address", "real_name", "location_coords", "ssn"}

    for k in sensitive_keys:
        if k in sanitized:
            sanitized[k] = "[REDACTED_PRIVACY]"

    return sanitized
