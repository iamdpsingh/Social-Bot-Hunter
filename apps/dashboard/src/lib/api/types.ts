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
