import { describe, it, expect } from "vitest";
import { getRiskBand, RISK_BANDS } from "../../../tokens/risk";

describe("Risk Tokens and Mapping", () => {
  it("maps scores >= 0.8 to critical risk", () => {
    expect(getRiskBand(0.85).band).toBe("critical");
    expect(getRiskBand(0.8).band).toBe("critical");
    expect(getRiskBand(1.0).band).toBe("critical");
  });

  it("maps scores between 0.6 and 0.79 to high risk", () => {
    expect(getRiskBand(0.75).band).toBe("high");
    expect(getRiskBand(0.6).band).toBe("high");
  });

  it("maps scores between 0.35 and 0.59 to medium risk", () => {
    expect(getRiskBand(0.45).band).toBe("medium");
    expect(getRiskBand(0.35).band).toBe("medium");
  });

  it("maps scores < 0.35 to low risk", () => {
    expect(getRiskBand(0.2).band).toBe("low");
    expect(getRiskBand(0.0).band).toBe("low");
  });

  it("maps null, undefined, or negative scores to insufficient_evidence", () => {
    expect(getRiskBand(null).band).toBe("insufficient_evidence");
    expect(getRiskBand(undefined).band).toBe("insufficient_evidence");
    expect(getRiskBand(-1).band).toBe("insufficient_evidence");
  });

  it("ensures each risk band definition has distinct iconography and accessible colors", () => {
    const bands = Object.values(RISK_BANDS);
    const colors = new Set(bands.map((b) => b.color));
    const icons = new Set(bands.map((b) => b.iconName));

    expect(colors.size).toBe(5);
    expect(icons.size).toBe(5);
  });
});
