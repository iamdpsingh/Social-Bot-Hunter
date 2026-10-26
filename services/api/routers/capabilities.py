"""Platform capability discovery endpoints."""

from fastapi import APIRouter
from sbh.contracts import Platform
from sbh.contracts.capabilities import default_registry

router = APIRouter(prefix="/capabilities", tags=["Capabilities"])


@router.get("")
def list_capabilities():
    registry = default_registry()
    items = []
    for cap in registry.all():
        items.append({
            "platform": cap.platform.value,
            "operation": cap.operation.value,
            "endpoint": cap.endpoint,
            "api_version": cap.api_version,
            "required_scopes": list(cap.required_scopes),
            "requires_approval": cap.requires_approval,
            "status": cap.status.value,
            "limitations": list(cap.limitations),
            "last_verified_at": cap.last_verified_at.isoformat() if cap.last_verified_at else None,
        })
    return {"capabilities": items, "total": len(items)}


@router.get("/{platform}")
def get_platform_capabilities(platform: str):
    try:
        p_enum = Platform(platform)
    except ValueError:
        return {"error": f"Unknown platform: {platform}", "capabilities": []}
    registry = default_registry()
    items = [
        {
            "operation": cap.operation.value,
            "endpoint": cap.endpoint,
            "api_version": cap.api_version,
            "required_scopes": list(cap.required_scopes),
            "requires_approval": cap.requires_approval,
            "status": cap.status.value,
            "limitations": list(cap.limitations),
            "last_verified_at": cap.last_verified_at.isoformat() if cap.last_verified_at else None,
        }
        for cap in registry.for_platform(p_enum)
    ]
    return {"platform": platform, "capabilities": items, "total": len(items)}
