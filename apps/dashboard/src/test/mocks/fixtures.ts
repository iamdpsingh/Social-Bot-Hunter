import type { ScanResponse, HealthResponse, CapabilityResponse, AuditEventResponse } from "../../lib/api/types";

export const mockScan: ScanResponse = {
  id: "scan_test_101",
  platform: "x",
  target_username: "target_account",
  status: "completed",
  created_at: "2026-11-04T12:00:00Z",
  risk_score: 82.5,
  risk_band: "HIGH",
  followers_count: 5000,
  following_count: 4200,
  suspicious_followers_count: 1400,
};

export const mockHealth: HealthResponse = {
  status: "ok",
  version: "0.1.0",
  database: "connected",
  components: {
    api: "healthy",
    database: "connected",
    worker_pool: "4 active workers",
  },
};

export const mockCapabilities: CapabilityResponse = {
  platforms: {
    x: { name: "X", status: "implemented", rate_limit: "15 req / 15 min" },
    instagram: { name: "Instagram", status: "implemented", rate_limit: "200 req / hour" },
  },
};

export const mockAudit: AuditEventResponse = {
  items: [
    {
      id: "audit_01",
      actor_id: "analyst_1",
      action: "investigation.launch",
      timestamp: "2026-11-04T12:30:00Z",
    },
  ],
  total: 1,
};
