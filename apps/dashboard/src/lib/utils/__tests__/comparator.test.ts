import { describe, it, expect } from "vitest";
import { compareValues, sortRecords } from "../comparator";

describe("Comparator utility", () => {
  it("sorts numbers ascending and descending", () => {
    expect(compareValues(10, 20, "asc")).toBeLessThan(0);
    expect(compareValues(10, 20, "desc")).toBeGreaterThan(0);
  });

  it("sorts records by key", () => {
    const items = [{ name: "Zack", score: 40 }, { name: "Alice", score: 90 }];
    const sorted = sortRecords(items, "name", "asc");
    expect(sorted[0].name).toBe("Alice");
    expect(sorted[1].name).toBe("Zack");
  });
});
