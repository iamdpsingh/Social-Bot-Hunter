import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { CoordinationClient } from "../coordination-client";
import * as coordinationHook from "../../../../../lib/hooks/use-coordination";

describe("CoordinationClient", () => {
  it("renders loading state", () => {
    vi.spyOn(coordinationHook, "useCoordination").mockReturnValue({
      coordination: null,
      isLoading: true,
      isError: false,
      error: null,
      mutate: vi.fn(),
    });
    render(<CoordinationClient scanId="s1" />);
    expect(screen.getByTestId("coordination-loading")).toBeInTheDocument();
  });

  it("renders populated coordination dashboard", () => {
    vi.spyOn(coordinationHook, "useCoordination").mockReturnValue({
      coordination: {
        scan_id: "s1",
        simhash_clusters: [],
        temporal_bursts: [],
        shared_hubs: [],
        total_coordinated_accounts: 14,
        overall_coordination_score: 0.85,
      },
      isLoading: false,
      isError: false,
      error: null,
      mutate: vi.fn(),
    });
    render(<CoordinationClient scanId="s1" />);
    expect(screen.getByTestId("coordination-page-client")).toBeInTheDocument();
    expect(screen.getByText("85%")).toBeInTheDocument();
    expect(screen.getByText("14")).toBeInTheDocument();
  });
});
