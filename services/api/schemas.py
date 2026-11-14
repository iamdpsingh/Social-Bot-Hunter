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


class ArchiveImportResponse(BaseModel):
    status: str
    archive_format: str = Field(..., description="Detected format (e.g. twitter_archive, ndjson, csv, generic_json)")
    file_count: int
    uncompressed_bytes: int
    platform_detected: str | None = None
    records_file: str | None = None
    extracted_path: str
    message: str
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
class SimHashClusterItem(BaseModel):
    cluster_id: str
    representative_text: str
    member_count: int
    account_ids: list[str]
    sample_texts: list[str]
    avg_pairwise_similarity: float
    max_hamming_distance: int


class TemporalBurstItem(BaseModel):
    burst_id: str
    start_timestamp: float
    end_timestamp: float
    post_count: int
    participating_accounts: list[str]
    coordination_lift: float


class SharedHubItem(BaseModel):
    target_id: str
    target_handle: str
    shared_by_count: int
    follower_account_ids: list[str]
    jaccard_overlap: float


class CoordinationSummaryResponse(BaseModel):
    scan_id: str
    simhash_clusters: list[SimHashClusterItem]
    temporal_bursts: list[TemporalBurstItem]
    shared_hubs: list[SharedHubItem]
    total_coordinated_accounts: int
    overall_coordination_score: float
class RetentionStatsResponse(BaseModel):
    total_scans: int
    oldest_scan_at: str | None = None
    retention_days: int
    expired_scans_count: int
    database_size_bytes: int
    auto_purge_enabled: bool


class RetentionPurgeRequest(BaseModel):
    retention_days: int = 90
    dry_run: bool = False


class RetentionPurgeResponse(BaseModel):
    scans_purged: int
    assessments_purged: int
    evidence_purged: int
    dry_run: bool
    purged_at: str


class PlatformQuotaStatus(BaseModel):
    platform: str
    daily_quota_limit: int
    quota_used_today: int
    quota_remaining: int
    rate_limit_rpm: int
    auth_state: str
    status: str

class ValidateUrlRequest(BaseModel):
    url: str
    platform_hint: str | None = None


class ValidateUrlResponse(BaseModel):
    platform: str
    handle: str
    canonical_url: str
    raw_url: str
    url_type: str
    channel_id: str | None = None
    is_canonical: bool


class ProbeAccountRequest(BaseModel):
    url: str
    platform_hint: str | None = None


class AccountProbeObservation(BaseModel):
    platform: str
    platform_account_id: str
    username: str | None = None
    display_name: str | None = None
    follower_count: int | None = None
    following_count: int | None = None
    post_count: int | None = None
    has_bio: bool | None = None
    has_profile_image: bool | None = None
    source_ref: str = ""


class ProbeAccountResponse(BaseModel):
    platform: str
    handle: str
    canonical_url: str
    outcome: str
    account: AccountProbeObservation | None = None
    limitation: str | None = None
    quota_consumed: int = 1
    daily_quota_remaining: int


class AdapterTelemetryRecord(BaseModel):
    platform: str
    endpoint: str
    total_calls: int
    error_count: int
    avg_latency_ms: float


class AdapterTelemetryResponse(BaseModel):
    telemetry: list[AdapterTelemetryRecord]


class MLFeatureAttributionItem(BaseModel):
    feature_name: str
    feature_value: float
    contribution: float
    relative_weight: float
    is_missing: bool
    explanation: str


class MLPredictRequest(BaseModel):
    account: dict[str, Any] = Field(..., description="Account profile dictionary containing metadata")
    contents: list[dict[str, Any]] = Field(default_factory=list, description="Recent posts for behavioral features")
    rule_score: float | None = Field(None, ge=0.0, le=100.0, description="Optional rule-based heuristic score to blend")
    evidence_coverage: float = Field(1.0, ge=0.0, le=1.0, description="Coverage ratio of observed rules evidence")
    alpha: float | None = Field(None, ge=0.0, le=1.0, description="Optional custom blend weight (1.0 = pure ML)")


class MLPredictResponse(BaseModel):
    account_id: str
    bot_probability: float
    is_bot: bool
    risk_band: str
    confidence: float
    raw_score: float
    top_positive_drivers: list[MLFeatureAttributionItem]
    top_negative_drivers: list[MLFeatureAttributionItem]
    missing_feature_count: int
    model_version: str


class MLModelInfoResponse(BaseModel):
    model_version: str
    algorithm: str
    trained_at: str
    training_samples: int
    metrics: dict[str, float]
    feature_count: int
    sha256_checksum: str
    author: str
    description: str


class CalibrationPointItem(BaseModel):
    bin_index: int
    mean_predicted_prob: float
    fraction_positives: float
    sample_count: int


class CalibrationCurveResponse(BaseModel):
    model_version: str
    points: list[CalibrationPointItem]
    ece: float
    brier_score: float


class FeatureImportanceResponse(BaseModel):
    model_version: str
    importances: dict[str, float]


# Day 12: Runtime Orchestration and Storage Management Schemas

class ProcessInfoSchema(BaseModel):
    name: str
    command: list[str]
    cwd: str
    port: int | None = None
    health_endpoint: str | None = None
    auto_restart: bool = True
    pid: int | None = None
    state: str
    restart_count: int
    started_at: float | None = None
    uptime_sec: float = 0.0


class RuntimeStatusResponse(BaseModel):
    supervisor_pid: int
    uptime_seconds: float
    services: dict[str, ProcessInfoSchema]
    queue: dict[str, int]
    storage: dict[str, Any]
    system: dict[str, Any]


class EnvCheckItemSchema(BaseModel):
    name: str
    passed: bool
    message: str
    details: dict[str, Any] | None = None


class EnvCheckResponse(BaseModel):
    all_passed: bool
    base_dir: str
    python_path: str
    virtual_env_active: bool
    checks: list[EnvCheckItemSchema]


class WorkerJobItem(BaseModel):
    job_id: str
    task_type: str
    payload: dict[str, Any]
    priority: int
    status: str
    created_at: str
    started_at: str | None = None
    completed_at: str | None = None
    attempts: int
    max_attempts: int
    worker_id: str | None = None
    error_message: str | None = None
    result_data: dict[str, Any] | None = None


class EnqueueJobRequest(BaseModel):
    task_type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    priority: int = 10
    max_attempts: int = 3


class EnqueueJobResponse(BaseModel):
    job_id: str
    task_type: str
    status: str
    priority: int
    created_at: str


class StorageDirectoryItem(BaseModel):
    category: str
    path: str
    file_count: int
    total_bytes: int
    total_mb: float
    oldest_timestamp: float | None = None
    newest_timestamp: float | None = None


class StorageStatsResponse(BaseModel):
    categories: dict[str, StorageDirectoryItem]
    total_files: int
    total_mb: float


class StoragePruneRequest(BaseModel):
    category: str | None = None
    max_age_days: int | None = 30
    max_size_mb: float | None = None
    keep_minimum: int = 3
    dry_run: bool = False


class StoragePruneReportItem(BaseModel):
    category: str
    scanned_count: int
    deleted_count: int
    bytes_reclaimed: int
    reclaimed_mb: float
    preserved_count: int
    dry_run: bool
    deleted_files: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class StoragePruneResponse(BaseModel):
    reports: list[StoragePruneReportItem]


class DatabaseBackupItem(BaseModel):
    backup_id: str
    database_type: str
    source_name: str
    filename: str
    relative_path: str
    size_bytes: int
    sha256: str
    table_counts: dict[str, int]
    created_at: str
    is_compressed: bool
    notes: str | None = None


class DatabaseBackupListResponse(BaseModel):
    backups: list[DatabaseBackupItem]


class CreateBackupRequest(BaseModel):
    output_filename: str | None = None
    compress: bool = False
    notes: str | None = None


class VerifyBackupRequest(BaseModel):
    backup_id: str


class VerifyBackupResponse(BaseModel):
    backup_id: str
    is_valid: bool
    message: str


# --- Security Audit Schemas ---

class SecretFindingItem(BaseModel):
    rule_id: str
    rule_name: str
    severity: str
    file_path: str
    line_number: int
    masked_value: str
    entropy: float


class SecretScanResponse(BaseModel):
    target_dir: str
    total_findings: int
    findings: list[SecretFindingItem]
    passed: bool


class PIIFindingItem(BaseModel):
    pii_type: str
    masked_value: str
    location: str
    line_number: int


class PrivacyScanResponse(BaseModel):
    passed: bool
    total_findings: int
    scanned_sources: int
    findings: list[PIIFindingItem]


class DependencyFindingItem(BaseModel):
    package_name: str
    installed_version: str
    ecosystem: str
    advisory_id: str
    severity: str
    patched_version: str
    summary: str


class DependencyEcosystemReport(BaseModel):
    ecosystem: str
    scanned_packages_count: int
    passed: bool
    findings: list[DependencyFindingItem]


class DependencyAuditResponse(BaseModel):
    passed: bool
    python: DependencyEcosystemReport
    node: DependencyEcosystemReport


class SecurityCheckItem(BaseModel):
    category: str
    check_id: str
    name: str
    passed: bool
    findings_count: int
    details: dict[str, Any]


class SecurityScorecardResponse(BaseModel):
    passed_audit: bool
    total_checks: int
    passed_checks: int
    failed_checks: int
    findings: list[SecretFindingItem]
    checks: list[SecurityCheckItem]


class AcceptanceCriterionSchema(BaseModel):
    criterion_id: str
    section: str
    title: str
    description: str
    verified: bool
    evidence_suite: str


class SystemReadinessResponse(BaseModel):
    all_verified: bool
    total_criteria: int
    verified_criteria: int
    compliance_percentage: float
    launch_status: str
    criteria: list[AcceptanceCriterionSchema]


class LaunchMilestoneSchema(BaseModel):
    day_number: int
    title: str
    status: str
    commits_count: int
    signoff_date: str


class LaunchChecklistResponse(BaseModel):
    total_days: int
    completed_days: int
    milestones: list[LaunchMilestoneSchema]


class BenchmarkSlaItemSchema(BaseModel):
    task_name: str
    p50_ms: float
    p90_ms: float
    p99_ms: float
    sla_limit_ms: float
    passed_sla: bool
    throughput_ops_sec: float


class SystemBenchmarkResponse(BaseModel):
    all_passed_sla: bool
    tasks_count: int
    benchmarks: list[BenchmarkSlaItemSchema]
