import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { PlatformAdapterCard } from "../../../components/adapters/platform-adapter-card";
import { PlatformQuotaStatus } from "../../../lib/api/types";

describe("Scenario: Quota Exhaustion Warning Flow", () => {
  it("displays critical warning banner and exhausted badge when limit reached", () => {
    const exhaustedQuota: PlatformQuotaStatus = {
      platform: "youtube",
      daily_quota_limit: 10000,
      quota_used_today: 10000,
      quota_remaining: 0,
      rate_limit_rpm: 600,
      auth_state: "api_key_configured",
      status: "exhausted",
    };

    render(<PlatformAdapterCard quota={exhaustedQuota} />);
    expect(screen.getByText(/exhausted/i)).toBeInTheDocument();
    expect(screen.getByText(/Daily quota exhausted. Requests paused until midnight UTC/i)).toBeInTheDocument();
  });
});
