import { render, screen } from "@testing-library/react";
import React from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { GraphPageClient } from "../graph-page-client";

describe("GraphPageClient component", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          scan_id: "scan_test",
          elements: { nodes: [{ data: { id: "a", score: 0.8 } }], edges: [] },
          node_count: 1,
          edge_count: 0,
          clusters: [],
        }),
      })
    );
  });

  it("renders page header, breadcrumbs, and view mode toggle", () => {
    render(<GraphPageClient scanId="scan_test" />);
    expect(screen.getByTestId("graph-page-client")).toBeInTheDocument();
    expect(screen.getByTestId("view-mode-toggle")).toBeInTheDocument();
  });
});
