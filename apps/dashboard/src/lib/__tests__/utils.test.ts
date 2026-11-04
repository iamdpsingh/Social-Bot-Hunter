import { describe, it, expect } from "vitest";
import { cn } from "../utils";

describe("cn class merging utility", () => {
  it("merges standard class strings and handles conditionals", () => {
    const result = cn("base-class", false && "ignored", "active-class");
    expect(result).toBe("base-class active-class");
  });

  it("deduplicates conflicting tailwind classes with precedence", () => {
    const result = cn("p-4 text-red-500", "p-6 text-blue-500");
    expect(result).toBe("p-6 text-blue-500");
  });
});
