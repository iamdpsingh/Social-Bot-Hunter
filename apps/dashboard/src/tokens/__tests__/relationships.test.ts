import { describe, it, expect } from "vitest";
import { RELATIONSHIP_TOKENS } from "../relationships";

describe("RELATIONSHIP_TOKENS", () => {
  it("defines follower, following, and mutual semantic styling", () => {
    expect(RELATIONSHIP_TOKENS.types.follower.label).toBe("Follower");
    expect(RELATIONSHIP_TOKENS.types.following.label).toBe("Following");
    expect(RELATIONSHIP_TOKENS.types.mutual.label).toBe("Mutual");
  });
});
