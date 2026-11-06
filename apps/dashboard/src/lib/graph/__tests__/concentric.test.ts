import { describe, expect, it } from "vitest";
import { getConcentricLevel } from "../concentric";

describe("getConcentricLevel", () => {
  it("calculates level based on risk score (0-10)", () => {
    expect(getConcentricLevel({ score: 0.95 })).toBe(10);
    expect(getConcentricLevel({ score: 0.52 })).toBe(5);
    expect(getConcentricLevel({ score: 0.12 })).toBe(1);
    expect(getConcentricLevel({ score: 0.0 })).toBe(0);
  });

  it("falls back to risk band when score is absent", () => {
    expect(getConcentricLevel({ band: "critical" })).toBe(10);
    expect(getConcentricLevel({ band: "high" })).toBe(8);
    expect(getConcentricLevel({ band: "medium" })).toBe(5);
    expect(getConcentricLevel({ band: "low" })).toBe(2);
    expect(getConcentricLevel({ band: "unknown" })).toBe(0);
  });
});
