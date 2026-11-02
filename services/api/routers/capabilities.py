"""Platform capability discovery endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from sbh.contracts import Platform
from sbh.contracts.capabilities import default_registry

from ..auth import require_authenticated
from ..schemas import CapabilityItem, CapabilityListResponse

router = APIRouter(prefix="/capabilities", tags=["Capabilities"])


@router.get("", response_model=CapabilityListResponse)
def list_capabilities(
    _: dict = Depends(require_authenticated),
):
    """List official platform capabilities, permission scopes, and verified endpoints."""
    registry = default_registry()
    items = []
    for cap in registry.all():
        items.append(
            CapabilityItem(
                platform=cap.platform.value,
                operation=cap.operation.value,
                endpoint=cap.endpoint,
                api_version=cap.api_version,
                required_scopes=list(cap.required_scopes),
                requires_approval=cap.requires_approval,
                status=cap.status.value,
                limitations=list(cap.limitations),
                last_verified_at=cap.last_verified_at.isoformat() if cap.last_verified_at else None,
            )
        )
    return CapabilityListResponse(capabilities=items, total=len(items))


@router.get("/{platform}", response_model=CapabilityListResponse)
def get_platform_capabilities(
    platform: str,
    _: dict = Depends(require_authenticated),
):
    """List capabilities for a specific social media platform."""
    try:
        p_enum = Platform(platform)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown platform: '{platform}'",
        ) from exc

    registry = default_registry()
    items = [
        CapabilityItem(
            platform=platform,
            operation=cap.operation.value,
            endpoint=cap.endpoint,
            api_version=cap.api_version,
            required_scopes=list(cap.required_scopes),
            requires_approval=cap.requires_approval,
            status=cap.status.value,
            limitations=list(cap.limitations),
            last_verified_at=cap.last_verified_at.isoformat() if cap.last_verified_at else None,
        )
        for cap in registry.for_platform(p_enum)
    ]
    return CapabilityListResponse(platform=platform, capabilities=items, total=len(items))
