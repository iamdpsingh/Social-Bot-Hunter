import { renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useGraphElements } from "../use-graph-elements";

describe("useGraphElements hook", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          scan_id: "scan_1",
          elements: { nodes: [{ data: { id: "a" } }], edges: [] },
          node_count: 1,
          edge_count: 0,
        }),
      })
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("fetches graph elements for scan id", async () => {
    const { result } = renderHook(() => useGraphElements("scan_1"));
    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data?.scan_id).toBe("scan_1");
    expect(result.current.data?.node_count).toBe(1);
    expect(result.current.error).toBeNull();
  });
});
