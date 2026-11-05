export type Platform = "instagram" | "x" | "tiktok" | "youtube" | "linkedin";

export type ScanStatus = "pending" | "running" | "complete" | "partial" | "failed" | "cancelled";

export type ScanType = "api_collection" | "dataset_import";

export type CollectionMode = "official_api" | "dataset_import" | "public_data";

export type DataOrigin = "api" | "imported" | "synthetic";

export interface ScanJob {
  id: string;
  scan_type: ScanType;
  collection_mode: CollectionMode;
  platform: Platform;
  status: ScanStatus;
  data_origin: DataOrigin;
  requested_by: string;
  created_at: string;
  started_at?: string | null;
  finished_at?: string | null;
  reference_time: string;
  config_version: string;
  config_sha256: string;
  status_detail?: Record<string, unknown>;
  failure_reason?: string | null;
  completeness?: string | null;
}

export interface ScanListResponse {
  scans: ScanJob[];
  total: number;
}

export interface ScanDetailResponse {
  scan: ScanJob;
}

export interface ScanProgressResponse {
  scan_id: string;
  status: ScanStatus;
  progress_pct: number;
  current_stage?: string | null;
  cursor_pos?: number | null;
  last_updated?: string | null;
}

export interface HealthResponse {
  status: "ok" | "degraded" | "error";
  database: "connected" | "disconnected";
  timestamp: string;
  version?: string;
}

export interface PlatformCapability {
  platform: Platform;
  operation: string;
  supported: boolean;
  endpoint?: string | null;
  required_permissions?: string[];
  limitations?: string[];
  verification_date?: string | null;
}

export interface CapabilitiesResponse {
  capabilities: PlatformCapability[];
  total: number;
}

export interface AuditEvent {
  id: string;
  actor: string;
  action: string;
  subject_type: string;
  subject_id: string;
  occurred_at: string;
  details?: Record<string, unknown>;
}

export interface AuditListResponse {
  events: AuditEvent[];
  total: number;
}

export interface CreateScanPayload {
  platform: Platform;
  target_account: string;
  scope: "quick" | "deep" | "comprehensive";
}

export interface AccountAssessment {
  id: string;
  scan_id: string;
  platform_account_id: string;
  pid: string;
  username?: string | null;
  status: "scored" | "insufficient_evidence";
  score?: number | null;
  band?: "critical" | "high" | "medium" | "low" | "insufficient_evidence" | null;
  evidence_coverage: number;
  features_available: number;
  features_total: number;
  contributions: Array<{ signal: string; weight: number; value: number; description?: string }>;
  limitations: string[];
}

export interface ProfileObservation {
  id: string;
  platform_account_id: string;
  username: string;
  display_name?: string | null;
  bio?: string | null;
  followers_count?: number | null;
  following_count?: number | null;
  posts_count?: number | null;
  is_verified?: boolean | null;
  has_default_avatar?: boolean | null;
  account_created_at?: string | null;
  observed_at: string;
}

export interface AccountDetailResponse {
  scan_id: string;
  account_id: string;
  assessment: AccountAssessment;
  profile_observation?: ProfileObservation | null;
  features: AccountFeature[];
}

export interface AccountEvidenceRecord {
  id: string;
  scan_id: string;
  subject_type: string;
  subject_id: string;
  evidence_type: string;
  summary: string;
  details: Record<string, unknown>;
  source_refs?: Array<Record<string, string>>;
}

export interface AccountEvidenceResponse {
  scan_id: string;
  account_id: string;
  evidence: AccountEvidenceRecord[];
  total: number;
}

export interface AccountFeature {
  id?: string;
  feature_name: string;
  feature_version?: string;
  category: string;
  value?: number | null;
  is_available: boolean;
  unavailable_reason?: string | null;
  details?: Record<string, unknown>;
}

export interface AccountFeaturesResponse {
  scan_id: string;
  account_id: string;
  features: AccountFeature[];
  total: number;
}

export interface AccountNeighborhoodEdge {
  source: string;
  target: string;
  relationship_type: string;
}

export interface AccountNeighborhoodResponse {
  scan_id: string;
  account_id: string;
  in_edges: AccountNeighborhoodEdge[];
  out_edges: AccountNeighborhoodEdge[];
  total_in: number;
  total_out: number;
}

export interface RelationshipEdge {
  source_account_id: string;
  target_account_id: string;
  relationship_type: "follower" | "following" | string;
  observed_at?: string | null;
}

export interface RelationshipListResponse {
  scan_id: string;
  total: number;
  offset: number;
  limit: number;
  relationships: RelationshipEdge[];
}

export interface AccountFilterParams {
  band?: string;
  status?: string;
  search?: string;
  sort_by?: "score_desc" | "score_asc" | "username_asc";
  limit?: number;
  offset?: number;
}

export interface ScanReportCluster {
  id: string;
  method: string;
  member_count: number;
  confidence: string;
  signal_strength: string;
  members: string[];
}

export interface ScanReportResponse {
  scan: ScanJob;
  is_synthetic: boolean;
  total_accounts: number;
  total_scored: number;
  total_insufficient_evidence: number;
  top_assessments: AccountAssessment[];
  clusters: ScanReportCluster[];
}
