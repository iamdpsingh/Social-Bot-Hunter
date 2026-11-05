import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import InvestigationsPage from "../page";

vi.mock("../../../lib/hooks/use-scans", () => ({
  useScans: () => ({
    scans: [
      {
        id: "scan_abc",
        target: "test_influencer",
        platform: "twitter",
        status: "completed",
        created_at: "2026-11-05T08:00:00Z",
      },
      {
        id: "scan_xyz",
        target: "crypto_bot_target",
        platform: "bluesky",
        status: "running",
        created_at: "2026-11-05T09:00:00Z",
      },
    ],
    isLoading: false,
    isError: false,
  }),
}));

describe("InvestigationsPage", () => {
  it("renders investigation archives and filters by status", () => {
    render(<InvestigationsPage />);

    expect(screen.getByText("Investigation Archives")).toBeInTheDocument();
    expect(screen.getByText("test_influencer")).toBeInTheDocument();
    expect(screen.getByText("crypto_bot_target")).toBeInTheDocument();

    // Filter by RUNNING
    fireEvent.click(screen.getByText("RUNNING"));
    expect(screen.queryByText("test_influencer")).not.toBeInTheDocument();
    expect(screen.getByText("crypto_bot_target")).toBeInTheDocument();
  });
});
