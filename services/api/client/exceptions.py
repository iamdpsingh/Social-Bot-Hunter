"""Client SDK exceptions hierarchy."""

from __future__ import annotations


class SBHClientError(Exception):
    """Base exception for Social Bot Hunter API client."""


class AuthenticationError(SBHClientError):
    """Raised on HTTP 401 Unauthorized."""


class AuthorizationError(SBHClientError):
    """Raised on HTTP 403 Forbidden."""


class NotFoundError(SBHClientError):
    """Raised on HTTP 404 Not Found."""


class RateLimitError(SBHClientError):
    """Raised on HTTP 429 Too Many Requests."""


class ValidationError(SBHClientError):
    """Raised on HTTP 422 Unprocessable Entity."""


class ServerError(SBHClientError):
    """Raised on HTTP 5xx Server Error."""
