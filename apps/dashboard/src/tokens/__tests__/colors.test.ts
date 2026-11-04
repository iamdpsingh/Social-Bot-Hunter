import { describe, it, expect } from "vitest";
import { PALETTE } from "../colors";

describe("Color Tokens", () => {
  it("contains primary brand colors and cyber midnight backgrounds", () => {
    expect(PALETTE.midnight[950]).toBe("#020617");
    expect(PALETTE.cyber[500]).toBe("#3B82F6");
    expect(PALETTE.risk.critical).toBe("#EF4444");
    expect(PALETTE.status.running).toBe("#3B82F6");
  });
});
