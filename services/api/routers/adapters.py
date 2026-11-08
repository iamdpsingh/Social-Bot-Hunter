"""FastAPI Router for Platform Adapters, Profile Probing, and Quota Telemetry."""

from __future__ import annotations

import time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from services.api.auth import get_current_user
from services.api.schemas import (
    AccountProbeObservation,
    AdapterTelemetryRecord,
    AdapterTelemetryResponse,
    PlatformQuotaStatus,
    ProbeAccountRequest,
    ProbeAccountResponse,
    UserResponse,
    ValidateUrlRequest,
    ValidateUrlResponse,
)

from sbh.adapters.errors import AdapterError, InvalidUrlError, UnsupportedPlatformError
from sbh.adapters.registry import default_registry
from sbh.adapters.telemetry import telemetry_manager
from sbh.adapters.url_validator import validate_profile_url
from sbh.adapters.x import XAdapter
from sbh.adapters.youtube import YouTubeAdapter
from sbh.contracts.adapter import AccessOutcome
from sbh.contracts.platforms import Platform

router = APIRouter(prefix="/adapters", tags=["Adapters"])


@router.post(
    "/validate-url",
    response_model=ValidateUrlResponse,
    summary="Validate and canonicalize social media profile URL",
)
def validate_url(
    req: ValidateUrlRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> ValidateUrlResponse:
    start_time = time.perf_counter()
    platform_hint: Platform | None = None
    if req.platform_hint:
        try:
            platform_hint = Platform(req.platform_hint.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid platform hint '{req.platform_hint}'",
            ) from None

    try:
        info = validate_profile_url(req.url, platform_hint=platform_hint)
        duration_ms = (time.perf_counter() - start_time) * 1000
        telemetry_manager.record_call(info.platform.value, "validate_url", duration_ms)
        return ValidateUrlResponse(
            platform=info.platform.value,
            handle=info.handle,
            canonical_url=info.canonical_url,
            raw_url=info.raw_url,
            url_type=info.url_type.value,
            channel_id=info.channel_id,
            is_canonical=info.is_canonical,
        )
    except (InvalidUrlError, UnsupportedPlatformError) as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        telemetry_manager.record_call(
            req.platform_hint or "unknown", "validate_url", duration_ms, is_error=True
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"URL validation failed: {e}",
        ) from e


@router.post(
    "/probe",
    response_model=ProbeAccountResponse,
    summary="Conduct preflight profile probe before launching scan",
)
def probe_account(
    req: ProbeAccountRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> ProbeAccountResponse:
    start_time = time.perf_counter()
    platform_hint: Platform | None = None
    if req.platform_hint:
        try:
            platform_hint = Platform(req.platform_hint.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid platform hint '{req.platform_hint}'",
            ) from None

    try:
        url_info = validate_profile_url(req.url, platform_hint=platform_hint)
    except (InvalidUrlError, UnsupportedPlatformError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    adapter = default_registry.get_adapter(url_info.platform)
    try:
        page = adapter.lookup_account(url_info.handle)
        duration_ms = (time.perf_counter() - start_time) * 1000
        telemetry_manager.record_call(url_info.platform.value, "lookup_account", duration_ms)

        obs: AccountProbeObservation | None = None
        if page.outcome == AccessOutcome.OK and page.items:
            it = page.items[0]
            obs = AccountProbeObservation(
                platform=it.platform,
                platform_account_id=it.platform_account_id,
                username=it.username,
                display_name=it.display_name,
                follower_count=it.follower_count,
                following_count=it.following_count,
                post_count=it.post_count,
                has_bio=it.has_bio,
                has_profile_image=it.has_profile_image,
                source_ref=it.source_ref,
            )

        quota_rem = 9999
        if isinstance(adapter, YouTubeAdapter):
            quota_rem = adapter.quota_tracker.remaining_units
        elif isinstance(adapter, XAdapter):
            quota_rem = adapter.rate_limiters["lookup"].remaining

        return ProbeAccountResponse(
            platform=url_info.platform.value,
            handle=url_info.handle,
            canonical_url=url_info.canonical_url,
            outcome=page.outcome.value,
            account=obs,
            limitation=page.limitation,
            quota_consumed=1,
            daily_quota_remaining=quota_rem,
        )
    except AdapterError as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        telemetry_manager.record_call(
            url_info.platform.value, "lookup_account", duration_ms, is_error=True
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
            if "Rate limit" in str(e)
            else status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "/quotas",
    response_model=list[PlatformQuotaStatus],
    summary="Get daily quota usage and limits across all platforms",
)
def get_adapter_quotas(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> list[PlatformQuotaStatus]:
    yt = default_registry.get_adapter(Platform.YOUTUBE)
    x = default_registry.get_adapter(Platform.X)

    quotas: list[PlatformQuotaStatus] = []
    if isinstance(yt, YouTubeAdapter):
        quotas.append(
            PlatformQuotaStatus(
                platform="youtube",
                daily_quota_limit=yt.quota_tracker.daily_limit,
                quota_used_today=yt.quota_tracker.units_used,
                quota_remaining=yt.quota_tracker.remaining_units,
                rate_limit_rpm=600,
                auth_state="api_key_configured",
                status="active" if not yt.quota_tracker.is_exhausted else "exhausted",
            )
        )

    if isinstance(x, XAdapter):
        lim = x.rate_limiters["lookup"]
        quotas.append(
            PlatformQuotaStatus(
                platform="x",
                daily_quota_limit=900,
                quota_used_today=max(0, lim.limit - lim.remaining),
                quota_remaining=lim.remaining,
                rate_limit_rpm=60,
                auth_state="bearer_token_configured",
                status="active" if not lim.is_limited else "rate_limited",
            )
        )

    return quotas


@router.get(
    "/telemetry",
    response_model=AdapterTelemetryResponse,
    summary="Retrieve performance telemetry across adapter endpoints",
)
def get_adapter_telemetry(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> AdapterTelemetryResponse:
    snapshot = telemetry_manager.get_snapshot()
    records = [
        AdapterTelemetryRecord(
            platform=str(it["platform"]),
            endpoint=str(it["endpoint"]),
            total_calls=int(it["total_calls"]),
            error_count=int(it["error_count"]),
            avg_latency_ms=float(it["avg_latency_ms"]),
        )
        for it in snapshot
    ]
    return AdapterTelemetryResponse(telemetry=records)
