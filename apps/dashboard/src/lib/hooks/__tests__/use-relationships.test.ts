import { describe, it, expect, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import { useRelationships } from "../use-relationships";

vi.mock("swr", () => ({
  default: () => ({
    data: {
      scan_id: "s1",
      total: 2,
      offset: 0,
      limit: 50,
      relationships: [
        { source_account_id: "u1", target_account_id: "u2", relationship_type: "follower" },
        { source_account_id: "u3", target_account_id: "u2", relationship_type: "follower" },
      ],
    },
    isLoading: false,
    error: null,
    mutate: vi.fn(),
  }),
}));

describe("useRelationships hook", () => {
  it("fetches directed relationship edges", () => {
    const { result } = renderHook(() => useRelationships("s1", { relationshipType: "follower" }));
    expect(result.current.isLoading).toBe(false);
    expect(result.current.relationships).toHaveLength(2);
  });
});
