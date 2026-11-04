import { describe, it, expect } from "vitest";
import { TYPOGRAPHY } from "../typography";

describe("Typography Tokens", () => {
  it("defines sans, mono font families and sizes", () => {
    expect(TYPOGRAPHY.fontFamily.sans).toBeDefined();
    expect(TYPOGRAPHY.fontFamily.mono).toBeDefined();
    expect(TYPOGRAPHY.fontSize.xs).toBeDefined();
    expect(TYPOGRAPHY.fontSize["2xl"]).toBeDefined();
  });
});
