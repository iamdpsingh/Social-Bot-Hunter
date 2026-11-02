"""Structured request logging with trace correlation and rate limiting middleware."""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from collections import defaultdict
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger("sbh.api.access")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class TraceCorrelationMiddleware(BaseHTTPMiddleware):
    """Assigns or propagates trace_id and records structured JSON access logs."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Response:
        trace_id = request.headers.get("X-Request-ID") or request.headers.get("X-Trace-ID") or str(uuid.uuid4())
        request.state.trace_id = trace_id

        start_time = time.perf_counter()
        client_ip = request.client.host if request.client else "unknown"

        response: Response
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            log_record = {
                "timestamp": datetime.now(UTC).isoformat(),
                "trace_id": trace_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": 500,
                "duration_ms": duration_ms,
                "client_ip": client_ip,
            }
            logger.error(json.dumps(log_record))
            raise

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Response-Time-Ms"] = str(duration_ms)

        log_record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "trace_id": trace_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "client_ip": client_ip,
        }
        logger.info(json.dumps(log_record))
        return response


class SimpleRateLimiterMiddleware(BaseHTTPMiddleware):
    """In-memory sliding window rate limiter per client IP.

    Configurable via environment variables. Disabled if SBH_DISABLE_RATE_LIMIT=true.
    """

    _instances: list[SimpleRateLimiterMiddleware] = []

    def __init__(
        self,
        app: Any,
        requests_per_minute: int = 300,
        login_requests_per_minute: int = 20,
    ) -> None:
        super().__init__(app)
        self.default_rpm = int(os.environ.get("SBH_RATE_LIMIT_RPM", str(requests_per_minute)))
        self.login_rpm = int(os.environ.get("SBH_LOGIN_RATE_LIMIT_RPM", str(login_requests_per_minute)))
        self.enabled = os.environ.get("SBH_DISABLE_RATE_LIMIT", "false").lower() not in ("true", "1")
        # Stores lists of timestamps per client IP
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._login_requests: dict[str, list[float]] = defaultdict(list)
        SimpleRateLimiterMiddleware._instances.append(self)

    @classmethod
    def reset(cls) -> None:
        """Clear cached request rate timestamps (useful for tests)."""
        for inst in cls._instances:
            inst._requests.clear()
            inst._login_requests.clear()

    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Response:
        if not self.enabled:
            return await call_next(request)

        # Allow health checks and docs without rate limit
        if request.url.path in ("/api/v1/health", "/docs", "/redoc", "/api/v1/openapi.json", "/"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        one_minute_ago = now - 60.0

        # Login endpoint protection against brute force
        if request.url.path == "/api/v1/auth/login" and request.method == "POST":
            timestamps = self._login_requests[client_ip]
            # Prune old timestamps
            self._login_requests[client_ip] = [ts for ts in timestamps if ts > one_minute_ago]
            if len(self._login_requests[client_ip]) >= self.login_rpm:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Too many login attempts. Please try again later.",
                        "error": "rate_limit_exceeded",
                    },
                    headers={"Retry-After": "60"},
                )
            self._login_requests[client_ip].append(now)
            return await call_next(request)

        # General API rate limiting
        timestamps = self._requests[client_ip]
        self._requests[client_ip] = [ts for ts in timestamps if ts > one_minute_ago]
        if len(self._requests[client_ip]) >= self.default_rpm:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Too many requests.",
                    "error": "rate_limit_exceeded",
                },
                headers={"Retry-After": "60"},
            )
        self._requests[client_ip].append(now)

        return await call_next(request)
