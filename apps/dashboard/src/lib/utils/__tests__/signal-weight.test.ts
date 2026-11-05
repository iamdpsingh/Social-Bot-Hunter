import { describe, it, expect } from "vitest";
import { formatSignalWeight, sortSignalsByImpact } from "../signal-weight";

describe("signal weight utilities", () => {
  it("formats weight as percentage", () => {
    expect(formatSignalWeight(0.35)).toBe("35%");
  });

  it("sorts signals by descending weight", () => {
    const list = [{ name: "A", weight: 0.1 }, { name: "B", weight: 0.5 }];
    const sorted = sortSignalsByImpact(list);
    expect(sorted[0].name).toBe("B");
  });
});
