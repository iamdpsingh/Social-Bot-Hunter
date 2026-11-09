import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { PlatformAdapterCard } from "../../../components/adapters/platform-adapter-card";
import { PlatformQuotaStatus } from "../../../lib/api/types";

describe("Scenario: TikTok Research API Flow", () => {
  it("renders TikTok adapter card with Research API details and quota metrics", () => {
    const tkQuota: PlatformQuotaStatus = {
      platform: "tiktok",
      daily_quota_limit: 5000,
      quota_used_today: 45,
      quota_remaining: 4955,
      rate_limit_rpm: 120,
      auth_state: "research_bearer_configured",
      status: "active",
    };

    render(<PlatformAdapterCard quota={tkQuota} />);
    expect(screen.getByText(/tiktok Data API/i)).toBeInTheDocument();
    expect(screen.getByText(/Research & Display API v2/i)).toBeInTheDocument();
    expect(screen.getByText(/5,000/i)).toBeInTheDocument();
  });
});
