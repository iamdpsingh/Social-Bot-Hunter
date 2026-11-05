import { describe, it, expect } from "vitest";
import { filterAccounts } from "../account-filter";
import type { AccountAssessment } from "../../api/types";

describe("filterAccounts utility", () => {
  const sampleAccounts: AccountAssessment[] = [
    {
      id: "1",
      scan_id: "s1",
      platform_account_id: "x_bot1",
      pid: "x_bot1",
      username: "elon_clone",
      status: "scored",
      score: 0.92,
      band: "critical",
      evidence_coverage: 1.0,
      features_available: 5,
      features_total: 5,
      contributions: [],
      limitations: [],
    },
    {
      id: "2",
      scan_id: "s1",
      platform_account_id: "x_human1",
      pid: "x_human1",
      username: "real_person",
      status: "scored",
      score: 0.15,
      band: "low",
      evidence_coverage: 1.0,
      features_available: 5,
      features_total: 5,
      contributions: [],
      limitations: [],
    },
  ];

  it("filters accounts by username substring", () => {
    const res = filterAccounts(sampleAccounts, "elon");
    expect(res).toHaveLength(1);
    expect(res[0].username).toBe("elon_clone");
  });

  it("filters accounts by risk band", () => {
    const res = filterAccounts(sampleAccounts, undefined, "critical");
    expect(res).toHaveLength(1);
    expect(res[0].band).toBe("critical");
  });
});
