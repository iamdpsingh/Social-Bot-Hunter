"""Sensitive data sanitization and log redaction utility."""

from __future__ import annotations

import re
from typing import Any

# Sensitive key patterns (case-insensitive substring match)
SENSITIVE_KEY_PATTERNS = [
    "pass",
    "secret",
    "token",
    "key",
    "auth",
    "credential",
    "bearer",
    "private",
    "cert",
    "signature",
]

# Sensitive value regexes (JWT tokens, bearer headers, private keys)
JWT_PATTERN = re.compile(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$")
BEARER_PATTERN = re.compile(r"(?i)Bearer\s+[A-Za-z0-9._~+/-]+=?")
API_KEY_PATTERN = re.compile(r"(?i)(api[_-]?key|access[_-]?token)['":=\s]+['"]?([a-zA-Z0-9_\-]{16,})['"]?")


class SecretSanitizer:
    """Sanitizer for redacting secrets from mappings, strings, and command lines."""

    def __init__(
        self,
        sensitive_keys: list[str] | None = None,
        mask_text: str = "[REDACTED]",
        preserve_prefix_len: int = 0,
    ) -> None:
        self.sensitive_keys = [k.lower() for k in (sensitive_keys or SENSITIVE_KEY_PATTERNS)]
        self.mask_text = mask_text
        self.preserve_prefix_len = preserve_prefix_len

    def is_key_sensitive(self, key_name: str) -> bool:
        """Check if a dictionary key name indicates sensitive contents."""
        lower = key_name.lower()
        return any(pat in lower for pat in self.sensitive_keys)

    def mask_value(self, val: str) -> str:
        """Mask a string value, optionally preserving prefix."""
        if not val:
            return val
        if self.preserve_prefix_len > 0 and len(val) > self.preserve_prefix_len:
            return f"{val[:self.preserve_prefix_len]}...{self.mask_text}"
        return self.mask_text

    def sanitize_string(self, text: str) -> str:
        """Redact known secret patterns from an arbitrary string."""
        if not text:
            return text
        sanitized = text
        sanitized = BEARER_PATTERN.sub(f"Bearer {self.mask_text}", sanitized)
        sanitized = API_KEY_PATTERN.sub(rf"={self.mask_text}", sanitized)
        if JWT_PATTERN.match(sanitized.strip()):
            return self.mask_text
        return sanitized

    def sanitize_mapping(self, data: dict[str, Any], depth: int = 0) -> dict[str, Any]:
        """Recursively sanitize dictionary keys and values."""
        if depth > 10:
            return {"[truncated]": "max_depth_exceeded"}

        out: dict[str, Any] = {}
        for k, v in data.items():
            if self.is_key_sensitive(str(k)):
                out[str(k)] = self.mask_value(str(v)) if v is not None else None
            elif isinstance(v, dict):
                out[str(k)] = self.sanitize_mapping(v, depth + 1)
            elif isinstance(v, list):
                out[str(k)] = self._sanitize_list(v, depth + 1)
            elif isinstance(v, str):
                out[str(k)] = self.sanitize_string(v)
            else:
                out[str(k)] = v
        return out

    def _sanitize_list(self, items: list[Any], depth: int) -> list[Any]:
        sanitized: list[Any] = []
        for item in items:
            if isinstance(item, dict):
                sanitized.append(self.sanitize_mapping(item, depth + 1))
            elif isinstance(item, list):
                sanitized.append(self._sanitize_list(item, depth + 1))
            elif isinstance(item, str):
                sanitized.append(self.sanitize_string(item))
            else:
                sanitized.append(item)
        return sanitized

    def sanitize_cmdline(self, argv: list[str]) -> list[str]:
        """Sanitize process command line arguments to avoid leaking tokens in ps."""
        result: list[str] = []
        skip_next = False
        for i, arg in enumerate(argv):
            if skip_next:
                result.append(self.mask_text)
                skip_next = False
                continue

            # Check flags like --token=<val> or --password=<val>
            if "=" in arg:
                key, val = arg.split("=", 1)
                if self.is_key_sensitive(key):
                    result.append(f"{key}={self.mask_text}")
                    continue

            # Check flags like --password <val>
            if arg.startswith("-") and self.is_key_sensitive(arg):
                result.append(arg)
                if i + 1 < len(argv) and not argv[i + 1].startswith("-"):
                    skip_next = True
                continue

            result.append(self.sanitize_string(arg))
        return result


_DEFAULT_SANITIZER = SecretSanitizer()


def sanitize_mapping(data: dict[str, Any]) -> dict[str, Any]:
    """Sanitize a dictionary using default secret sanitizer."""
    return _DEFAULT_SANITIZER.sanitize_mapping(data)


def sanitize_cmdline(argv: list[str]) -> list[str]:
    """Sanitize command line argument vector."""
    return _DEFAULT_SANITIZER.sanitize_cmdline(argv)


def format_safe_env(env: dict[str, str] | None = None) -> dict[str, str]:
    """Return environment variables with sensitive values redacted."""
    import os

    source = env if env is not None else dict(os.environ)
    sanitizer = SecretSanitizer()
    return sanitizer.sanitize_mapping(source)
