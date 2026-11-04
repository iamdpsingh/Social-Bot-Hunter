import { describe, it, expect } from "vitest";
import { colors } from "../colors";

describe("Color Tokens", () => {
  it("contains primary brand colors and cyber midnight backgrounds", () => {
    expect(colors.primary).toBeDefined();
    expect(colors.background).toBe("#0b0f19");
    expect(colors.neonCyan).toBe("#06b6d4");
    expect(colors.neonPurple).toBe("#a855f7");
  });
});
