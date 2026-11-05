import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import InvestigationDetailPage from "../page";

vi.mock("next/navigation", () => ({
  useParams: () => ({ id: "scan_workspace_01" }),
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock("../../../lib/hooks/use-investigation", () => ({
  useInvestigation: () => ({
    investigation: {
      id: "scan_workspace_01",
      target: "target_botnet",
      platform: "twitter",
      status: "completed",
      accounts_analyzed: 150,
      bot_count: 42,
    },
    isLoading: false,
    isError: false,
  }),
}));

vi.mock("../../../lib/hooks/use-relationships", () => ({
  useRelationships: () => ({
    relationships: [
      {
        source_id: "acc_1",
        target_id: "target_botnet",
        relationship_type: "follower",
        confidence: 0.95,
      },
    ],
    totalCount: 1,
    isLoading: false,
  }),
}));

describe("InvestigationDetailPage", () => {
  it("renders investigation workspace with tabs and switches view", () => {
    render(<InvestigationDetailPage />);

    expect(screen.getByTestId("investigation-workspace")).toBeInTheDocument();
    expect(screen.getByText("target_botnet")).toBeInTheDocument();

    // Switch to explorer tab
    const explorerTab = screen.getByText(/Followers \/ Following/);
    fireEvent.click(explorerTab);
    expect(screen.getByPlaceholderText(/Search by handle or account ID/)).toBeInTheDocument();
  });
});
