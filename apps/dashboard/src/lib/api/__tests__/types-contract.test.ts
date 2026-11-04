import { describe, it, expect } from "vitest";
import type { ScanJob, HealthResponse, Platform } from "../types";

describe("API Types Contract", () => {
  it("conforms to backend schema structure for ScanJob", () => {
    const scan: ScanJob = {
      id: "scan_test",
      platform: "x" as Platform,
      scan_type: "api_collection",
      collection_mode: "official_api",
      status: "complete",
      data_origin: "api",
      requested_by: "analyst_1",
      created_at: "2026-11-04T00:00:00Z",
      reference_time: "2026-11-04T00:00:00Z",
      config_version: "v1.0",
      config_sha256: "abc123sha",
    };
    expect(scan.status).toBe("complete");
    expect(scan.platform).toBe("x");
  });

  it("conforms to HealthResponse schema", () => {
    const health: HealthResponse = {
      status: "ok",
      version: "0.1.0",
      database: "connected",
      timestamp: "2026-11-04T00:00:00Z",
    };
    expect(health.database).toBe("connected");
  });
});
