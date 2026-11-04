import { describe, it, expect } from "vitest";
import type { ScanResponse, HealthResponse, PlatformType } from "../types";

describe("API Types Contract", () => {
  it("conforms to backend schema structure for ScanResponse", () => {
    const scan: ScanResponse = {
      id: "scan_test",
      platform: "x" as PlatformType,
      target_username: "target",
      status: "completed",
      created_at: "2026-11-04T00:00:00Z",
      risk_score: 42.5,
    };
    expect(scan.status).toBe("completed");
    expect(scan.risk_score).toBe(42.5);
  });

  it("conforms to HealthResponse schema", () => {
    const health: HealthResponse = {
      status: "ok",
      version: "0.1.0",
      database: "connected",
    };
    expect(health.database).toBe("connected");
  });
});
