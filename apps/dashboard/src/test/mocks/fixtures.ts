import type { ScanJob, HealthResponse, CapabilitiesResponse, AuditListResponse } from "../../lib/api/types";

export const mockScan: ScanJob = {
  id: "scan_test_101",
  platform: "x",
  scan_type: "api_collection",
  collection_mode: "official_api",
  status: "complete",
  data_origin: "synthetic",
  requested_by: "analyst_1",
  created_at: "2026-11-04T12:00:00Z",
  reference_time: "2026-11-04T12:00:00Z",
  config_version: "v1.0",
  config_sha256: "abc123sha",
};

export const mockHealth: HealthResponse = {
  status: "ok",
  version: "0.1.0",
  database: "connected",
  timestamp: "2026-11-04T12:00:00Z",
};

export const mockCapabilities: CapabilitiesResponse = {
  capabilities: [
    {
      platform: "x",
      operation: "read_profile",
      supported: true,
      endpoint: "https://api.x.com/2/users/by/username/:username",
    },
    {
      platform: "instagram",
      operation: "read_profile",
      supported: true,
      endpoint: "https://graph.instagram.com/me",
    },
  ],
  total: 2,
};

export const mockAudit: AuditListResponse = {
  events: [
    {
      id: "audit_01",
      actor: "analyst_1",
      action: "investigation.launch",
      subject_type: "scan",
      subject_id: "scan_test_101",
      occurred_at: "2026-11-04T12:30:00Z",
    },
  ],
  total: 1,
};
