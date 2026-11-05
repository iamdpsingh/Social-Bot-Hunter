import { describe, it, expect } from "vitest";
import { ENDPOINTS } from "../endpoints";

describe("ENDPOINTS Registry", () => {
  it("interpolates scan and account routes accurately", () => {
    expect(ENDPOINTS.scans.relationships("s_10")).toContain("/scans/s_10/relationships");
    expect(ENDPOINTS.scans.exportCsv("s_10")).toContain("/scans/s_10/export/csv");
    expect(ENDPOINTS.scans.exportJson("s_10")).toContain("/scans/s_10/export/json");
    expect(ENDPOINTS.accounts.list("s_10")).toContain("/scans/s_10/accounts");
    expect(ENDPOINTS.accounts.detail("s_10", "acc_99")).toContain("/scans/s_10/accounts/acc_99");
    expect(ENDPOINTS.accounts.evidence("s_10", "acc_99")).toContain("/scans/s_10/accounts/acc_99/evidence");
  });
});
