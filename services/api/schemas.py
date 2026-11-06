"""Pydantic v2 schemas for all API request and response payloads."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


# -----------------------------------------------------------------------------
# Base / Generic
# -----------------------------------------------------------------------------
class HealthResponse(BaseModel):
    status: str = "ok"
    database: str = "connected"
    timestamp: str
    version: str = "0.1.0"


class RootResponse(BaseModel):
    service: str = "Social Bot Hunter API"
    docs: str = "/docs"
    health: str = "/api/v1/health"
    version: str = "0.1.0"


# -----------------------------------------------------------------------------
# Auth & User Schemas
# -----------------------------------------------------------------------------
class UserSummary(BaseModel):
    id: str
    username: str
    role: str
    full_name: str | None = None


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1, max_length=256)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserSummary


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)


class RevokeTokenRequest(BaseModel):
    token: str | None = None


class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64, pattern=r"^[a-zA-Z0-9_\-\.]+$")
    password: str = Field(..., min_length=8, max_length=256)
    role: str = Field(..., description="admin, investigator, auditor, or readonly")
    full_name: str | None = Field(None, max_length=128)


class UserUpdateRequest(BaseModel):
    full_name: str | None = Field(None, max_length=128)
    role: str | None = Field(None, description="admin, investigator, auditor, or readonly")
    is_active: bool | None = None
    password: str | None = Field(None, min_length=8, max_length=256)


class UserResponse(BaseModel):
    id: str
    username: str
    role: str
    full_name: str | None = None
    is_active: bool
    created_at: str
    updated_at: str


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int
    limit: int
    offset: int


# -----------------------------------------------------------------------------
# Scan Schemas
# -----------------------------------------------------------------------------
class ScanCreateRequest(BaseModel):
    platform: str = Field(..., pattern="^(instagram|x|tiktok|youtube|linkedin)$")
    target_account: str = Field(..., min_length=1)
    scope: str = Field(default="standard", pattern="^(quick|standard|deep|comprehensive)$")
    config_overrides: dict[str, Any] = Field(default_factory=dict)


class ScanCreateResponse(BaseModel):
    scan_id: str
    platform: str
    target_account: str
    scope: str
    status: str = "pending"


class ScanListResponse(BaseModel):
    scans: list[dict[str, Any]]
    total: int


class ScanDetailResponse(BaseModel):
    scan: dict[str, Any]


class ScanReportResponse(BaseModel):
    scan: dict[str, Any]
    is_synthetic: bool
    total_accounts: int
    total_scored: int
    total_insufficient_evidence: int
    top_assessments: list[dict[str, Any]]
    clusters: list[dict[str, Any]]


class ScanDeleteResponse(BaseModel):
    status: str = "deleted"
    scan_id: str
    deleted_rows: dict[str, int]


class ScanCancelResponse(BaseModel):
    scan_id: str
    status: str = "cancelled"
    message: str = "Scan cancellation requested"


class ScanRetryResponse(BaseModel):
    scan_id: str
    status: str = "pending"
    message: str = "Scan queued for retry"


class ScanProgressResponse(BaseModel):
    scan_id: str
    status: str
    stage: str
    progress_pct: float
    latest_checkpoint: dict[str, Any] | None = None


class ScanDiffResponse(BaseModel):
    scan_a: str
    scan_b: str
    diff: dict[str, Any]
    notes: str


# -----------------------------------------------------------------------------
# Account Schemas
# -----------------------------------------------------------------------------
class AccountListResponse(BaseModel):
    scan_id: str
    total: int
    offset: int
    limit: int
    accounts: list[dict[str, Any]]


class AccountDetailResponse(BaseModel):
    scan_id: str
    account_id: str
    assessment: dict[str, Any]
    profile_observation: dict[str, Any] | None = None
    features: list[dict[str, Any]]


class AccountEvidenceResponse(BaseModel):
    scan_id: str
    account_id: str
    evidence: list[dict[str, Any]]
    total: int


class AccountFeaturesResponse(BaseModel):
    scan_id: str
    account_id: str
    features: list[dict[str, Any]]
    total: int


class AccountNeighborhoodResponse(BaseModel):
    scan_id: str
    account_id: str
    in_edges: list[dict[str, Any]]
    out_edges: list[dict[str, Any]]
    total_in: int
    total_out: int


# -----------------------------------------------------------------------------
# Network Schemas
# -----------------------------------------------------------------------------
class ClusterListResponse(BaseModel):
    scan_id: str
    clusters: list[dict[str, Any]]
    total: int


class CytoscapeGraphElements(BaseModel):
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]


class CytoscapeGraphResponse(BaseModel):
    scan_id: str
    elements: CytoscapeGraphElements
    node_count: int
    edge_count: int


# -----------------------------------------------------------------------------
# Capability Schemas
# -----------------------------------------------------------------------------
class CapabilityItem(BaseModel):
    platform: str | None = None
    operation: str
    endpoint: str | None = None
    api_version: str | None = None
    required_scopes: list[str]
    requires_approval: bool | None = None
    status: str
    limitations: list[str]
    last_verified_at: str | None = None


class CapabilityListResponse(BaseModel):
    capabilities: list[CapabilityItem]
    total: int
    platform: str | None = None


# -----------------------------------------------------------------------------
# Import Schemas
# -----------------------------------------------------------------------------
class ImportDatasetRequest(BaseModel):
    source_path: str = Field(..., min_length=1)
    requested_by: str = "api-user"
    allow_resume_running: bool = False


class ImportResponse(BaseModel):
    status: str
    scan_id: str
    already_imported: bool
    summary: dict[str, Any]
    is_synthetic: bool = False


# -----------------------------------------------------------------------------
# Audit Schemas
# -----------------------------------------------------------------------------
class AuditEventResponse(BaseModel):
    id: str
    occurred_at: str
    actor: str
    action: str
    subject_type: str
    subject_id: str | None = None
    details: dict[str, Any]


class AuditListResponse(BaseModel):
    events: list[AuditEventResponse]
    total: int
    limit: int
    offset: int


class RelationshipItem(BaseModel):
    source_account_id: str
    target_account_id: str
    relationship_type: str
    observed_at: str | None = None


class RelationshipListResponse(BaseModel):
    scan_id: str
    total: int
    offset: int
    limit: int
    relationships: list[RelationshipItem]


class AccountExportBundleResponse(BaseModel):
    scan: dict[str, Any]
    exported_at: str
    is_synthetic: bool
    total_accounts: int
    accounts: list[dict[str, Any]]
    clusters: list[dict[str, Any]]


class NodeNeighborItem(BaseModel):
    node_id: str
    direction: str
    relationship_type: str = "follows"
    risk_score: float | None = None
    risk_band: str | None = None


class NodeNeighborsResponse(BaseModel):
    scan_id: str
    center_node_id: str
    direction: str
    radius: int
    neighbors: list[NodeNeighborItem]
    total: int


class GraphMetricsResponse(BaseModel):
    scan_id: str
    node_count: int
    edge_count: int
    density: float
    reciprocity: float
    weakly_connected_components: int
    strongly_connected_components: int
    avg_in_degree: float
    avg_out_degree: float


class GraphExportBundleResponse(BaseModel):
    scan_id: str
    format: str
    elements: CytoscapeGraphElements
    metrics: dict[str, Any]
    exported_at: str
