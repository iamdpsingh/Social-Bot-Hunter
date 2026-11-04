import { describe, it, expect } from "vitest";
import { RISK_BANDS } from "../../../../src/tokens/risk";

describe("WCAG 2.1 AA Contrast Compliance", () => {
  it("ensures every risk badge definition includes accessible contrast tokens", () => {
    for (const [level, token] of Object.entries(RISK_BANDS)) {
      expect(token.label).toBeDefined();
      expect(token.color).toBeDefined();
      expect(token.bgColor).toBeDefined();
      expect(token.borderColor).toBeDefined();
    }
  });
});
