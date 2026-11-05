import { describe, it, expect } from "vitest";
import { TABLE_CONFIG } from "../table-virtualization";

describe("TABLE_CONFIG tokens", () => {
  it("defines constant row height and pagination options", () => {
    expect(TABLE_CONFIG.rowHeight).toBe(52);
    expect(TABLE_CONFIG.pageSizeOptions).toContain(50);
  });
});
