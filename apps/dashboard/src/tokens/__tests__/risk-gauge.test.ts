import { describe, it, expect } from "vitest";
import { RISK_GAUGE_TOKENS } from "../risk-gauge";

describe("RISK_GAUGE_TOKENS", () => {
  it("defines proportional dimensions across sm, md, and lg presets", () => {
    expect(RISK_GAUGE_TOKENS.sizes.sm.width).toBe(96);
    expect(RISK_GAUGE_TOKENS.sizes.md.width).toBe(140);
    expect(RISK_GAUGE_TOKENS.sizes.lg.width).toBe(180);
    expect(RISK_GAUGE_TOKENS.bands.critical).toBe("#EF4444");
  });
});
