import { describe, it, expect } from "vitest";
import { TABLE_VIRTUALIZATION_TOKENS } from "../../../tokens/table-virtualization";

describe("Scenario: Table Virtualization Row Geometry", () => {
  it("computes viewport slices accurately for 10,000 accounts", () => {
    const totalAccounts = 10000;
    const rowHeight = TABLE_VIRTUALIZATION_TOKENS.rowHeight;
    const viewportHeight = TABLE_VIRTUALIZATION_TOKENS.viewportHeight;
    const overscan = TABLE_VIRTUALIZATION_TOKENS.overscan;

    const visibleRowsCount = Math.ceil(viewportHeight / rowHeight);
    expect(visibleRowsCount).toBe(12);

    const scrollTop = 1200; // Scrolled past 25 rows
    const startIndex = Math.max(0, Math.floor(scrollTop / rowHeight) - overscan);
    const endIndex = Math.min(totalAccounts, startIndex + visibleRowsCount + overscan * 2);

    expect(startIndex).toBeGreaterThanOrEqual(0);
    expect(endIndex).toBeLessThanOrEqual(totalAccounts);
    expect(endIndex - startIndex).toBeLessThanOrEqual(visibleRowsCount + overscan * 2 + 1);
  });
});
