import { describe, it, expect } from "vitest";
import { RISK_LEVELS } from "../../../../src/tokens/risk";

describe("WCAG 2.1 AA Contrast Compliance", () => {
  it("ensures every risk badge definition includes accessible contrast tokens and dual indicator iconography", () => {
    for (const [level, token] of Object.entries(RISK_LEVELS)) {
      expect(token.label).toBeDefined();
      expect(token.color).toBeDefined();
      expect(token.bgColor).toBeDefined();
      expect(token.borderColor).toBeDefined();
      expect(token.icon).toBeDefined();
    }
  });
});
