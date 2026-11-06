import { renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useGraphMetrics } from "../use-graph-metrics";

describe("useGraphMetrics hook", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          scan_id: "scan_1",
          node_count: 50,
          edge_count: 100,
          density: 0.04,
          reciprocity: 0.15,
          weakly_connected_components: 3,
          strongly_connected_components: 10,
          avg_in_degree: 2.0,
          avg_out_degree: 2.0,
        }),
      })
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("fetches topology metrics", async () => {
    const { result } = renderHook(() => useGraphMetrics("scan_1"));
    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.metrics?.node_count).toBe(50);
    expect(result.current.metrics?.density).toBe(0.04);
  });
});
