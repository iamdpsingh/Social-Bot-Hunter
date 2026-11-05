import { describe, it, expect } from "vitest";
import type { AccountAssessment, RelationshipEdge, ScanReportResponse } from "../types";

describe("Investigation Types Compliance", () => {
  it("validates AccountAssessment properties", () => {
    const assessment: AccountAssessment = {
      id: "ass_1",
      scan_id: "scan_10",
      platform_account_id: "p_10",
      pid: "p_10",
      username: "bot_101",
      status: "scored",
      score: 0.88,
      band: "critical",
      evidence_coverage: 0.95,
      features_available: 12,
      features_total: 12,
      contributions: [{ signal: "fast_follow", weight: 0.3, value: 0.9 }],
      limitations: [],
    };
    expect(assessment.band).toBe("critical");
    expect(assessment.score).toBe(0.88);
  });

  it("validates RelationshipEdge properties", () => {
    const edge: RelationshipEdge = {
      source_account_id: "acc_a",
      target_account_id: "acc_b",
      relationship_type: "follower",
      observed_at: "2026-11-05T09:00:00Z",
    };
    expect(edge.relationship_type).toBe("follower");
  });
});
