import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { PlatformAdapterCard } from "../../../components/adapters/platform-adapter-card";
import { PlatformQuotaStatus } from "../../../lib/api/types";

describe("Scenario: Instagram Business Discovery Flow", () => {
  it("renders Instagram adapter card with Graph API details and quota metrics", () => {
    const igQuota: PlatformQuotaStatus = {
      platform: "instagram",
      daily_quota_limit: 4800,
      quota_used_today: 120,
      quota_remaining: 4680,
      rate_limit_rpm: 200,
      auth_state: "graph_api_token_configured",
      status: "active",
    };

    render(<PlatformAdapterCard quota={igQuota} />);
    expect(screen.getByText(/instagram Data API/i)).toBeInTheDocument();
    expect(screen.getByText(/Graph API v21.0 Business Discovery/i)).toBeInTheDocument();
    expect(screen.getByText(/4,800/i)).toBeInTheDocument();
  });
});
