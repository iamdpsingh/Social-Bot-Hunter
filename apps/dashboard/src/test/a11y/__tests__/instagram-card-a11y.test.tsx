import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { PlatformAdapterCard } from "../../../components/adapters/platform-adapter-card";
import { PlatformQuotaStatus } from "../../../lib/api/types";

describe("A11y: Instagram Adapter Card", () => {
  it("provides accessible progressbar and role labels for Instagram quota", () => {
    const igQuota: PlatformQuotaStatus = {
      platform: "instagram",
      daily_quota_limit: 4800,
      quota_used_today: 400,
      quota_remaining: 4400,
      rate_limit_rpm: 200,
      auth_state: "graph_api_token_configured",
      status: "active",
    };

    render(<PlatformAdapterCard quota={igQuota} />);
    const bar = screen.getByRole("progressbar");
    expect(bar).toBeInTheDocument();
    expect(bar).toHaveAttribute("aria-label", "instagram API Quota Usage");
  });
});
