import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { PlatformAdapterCard } from "../../../components/adapters/platform-adapter-card";
import { PlatformQuotaStatus } from "../../../lib/api/types";

describe("A11y: TikTok Adapter Card", () => {
  it("provides accessible progressbar and role labels for TikTok quota", () => {
    const tkQuota: PlatformQuotaStatus = {
      platform: "tiktok",
      daily_quota_limit: 5000,
      quota_used_today: 250,
      quota_remaining: 4750,
      rate_limit_rpm: 120,
      auth_state: "research_bearer_configured",
      status: "active",
    };

    render(<PlatformAdapterCard quota={tkQuota} />);
    const bar = screen.getByRole("progressbar");
    expect(bar).toBeInTheDocument();
    expect(bar).toHaveAttribute("aria-label", "tiktok API Quota Usage");
  });
});
