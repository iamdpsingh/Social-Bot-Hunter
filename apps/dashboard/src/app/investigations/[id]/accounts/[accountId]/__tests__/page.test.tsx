import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import AccountDetailPage from "../page";

vi.mock("next/navigation", () => ({
  useParams: () => ({ id: "scan_workspace_01", accountId: "bot_suspect_42" }),
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock("../../../../../lib/hooks/use-account-detail", () => ({
  useAccountDetail: () => ({
    account: {
      account: {
        id: "bot_suspect_42",
        username: "bot_suspect_42",
        platform: "twitter",
      },
      assessment: {
        account_id: "bot_suspect_42",
        risk_score: 0.89,
        risk_band: "high",
        confidence: 0.94,
      },
      observation: {
        observed_at: "2026-11-05T08:00:00Z",
        followers_count: 50,
        following_count: 4500,
        posts_count: 12,
      },
    },
    isLoading: false,
  }),
}));

vi.mock("../../../../../lib/hooks/use-account-evidence", () => ({
  useAccountEvidence: () => ({
    evidence: [
      {
        id: "ev_1",
        rule_name: "High following ratio",
        score: 0.9,
        weight: 0.35,
        confidence: 0.9,
        summary: "Follows 4500 with only 50 followers",
        observed_data: {},
      },
    ],
    isLoading: false,
  }),
}));

vi.mock("../../../../../lib/hooks/use-account-neighborhood", () => ({
  useAccountNeighborhood: () => ({
    neighborhood: {
      target_account_id: "bot_suspect_42",
      incoming: [],
      outgoing: [],
    },
    isLoading: false,
  }),
}));

describe("AccountDetailPage", () => {
  it("renders account deep dive with profile, risk gauge, signals and evidence", () => {
    render(<AccountDetailPage />);

    expect(screen.getByTestId("account-detail-page")).toBeInTheDocument();
    expect(screen.getByText("@bot_suspect_42")).toBeInTheDocument();
    expect(screen.getByText("Overall Risk Evaluation")).toBeInTheDocument();
    expect(screen.getByText("Contributing Heuristic Signals")).toBeInTheDocument();
  });
});
