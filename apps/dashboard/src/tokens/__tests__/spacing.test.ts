import { describe, it, expect } from "vitest";
import { SPACING } from "../spacing";

describe("Spacing Tokens", () => {
  it("contains container and sidebar layout dimensions", () => {
    expect(SPACING.container.maxWidth).toBe("1440px");
    expect(SPACING.sidebar.width).toBe("260px");
    expect(SPACING.header.height).toBe("64px");
  });
});
