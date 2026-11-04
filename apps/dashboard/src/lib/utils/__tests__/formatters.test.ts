import { describe, it, expect } from "vitest";
import { formatNumber, formatDuration } from "../formatters";

describe("Formatters utility", () => {
  it("formats numbers with comma separators", () => {
    expect(formatNumber(1250000)).toBe("1,250,000");
    expect(formatNumber(42)).toBe("42");
  });

  it("formats seconds into human readable duration", () => {
    expect(formatDuration(45)).toBe("45s");
    expect(formatDuration(125)).toBe("2m 5s");
  });
});
