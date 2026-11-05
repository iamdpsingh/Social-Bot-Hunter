import { describe, it, expect, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import { useAccountNeighborhood } from "../use-account-neighborhood";

vi.mock("swr", () => ({
  default: () => ({
    data: {
      scan_id: "s1",
      account_id: "a1",
      in_edges: [{ source: "u9", target: "a1", relationship_type: "follower" }],
      out_edges: [{ source: "a1", target: "u8", relationship_type: "following" }],
      total_in: 1,
      total_out: 1,
    },
    isLoading: false,
    error: null,
    mutate: vi.fn(),
  }),
}));

describe("useAccountNeighborhood hook", () => {
  it("fetches 1-hop inbound and outbound edges", () => {
    const { result } = renderHook(() => useAccountNeighborhood("s1", "a1"));
    expect(result.current.isLoading).toBe(false);
    expect(result.current.totalIn).toBe(1);
    expect(result.current.totalOut).toBe(1);
  });
});
