import { describe, it, expect } from "vitest";
import { spacing } from "../spacing";

describe("Spacing Tokens", () => {
  it("contains structured 4px grid spacing values", () => {
    expect(spacing[1]).toBe("0.25rem");
    expect(spacing[4]).toBe("1rem");
    expect(spacing[8]).toBe("2rem");
  });
});
