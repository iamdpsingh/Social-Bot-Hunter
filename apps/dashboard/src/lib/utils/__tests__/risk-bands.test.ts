import { describe, it, expect } from "vitest";
import { scoreToRiskBand, getRiskBandLabel } from "../risk-bands";

describe("Risk Bands utility", () => {
  it("correctly maps numeric scores to risk bands", () => {
    expect(scoreToRiskBand(5)).toBe("MINIMAL");
    expect(scoreToRiskBand(25)).toBe("LOW");
    expect(scoreToRiskBand(55)).toBe("MEDIUM");
    expect(scoreToRiskBand(75)).toBe("HIGH");
    expect(scoreToRiskBand(95)).toBe("CRITICAL");
  });

  it("returns human readable risk band label", () => {
    expect(getRiskBandLabel("MINIMAL")).toBe("Minimal Risk");
    expect(getRiskBandLabel("CRITICAL")).toBe("Critical Risk");
  });
});
