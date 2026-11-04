import { describe, it, expect } from "vitest";
import { typography } from "../typography";

describe("Typography Tokens", () => {
  it("defines sans, mono font families and sizes", () => {
    expect(typography.fontFamily.sans).toBeDefined();
    expect(typography.fontFamily.mono).toBeDefined();
    expect(typography.fontSize.xs).toBeDefined();
    expect(typography.fontSize.xl).toBeDefined();
  });
});
