import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { PlatformAdapterCard } from "../platform-adapter-card";
import { PlatformQuotaStatus } from "../../../lib/api/types";

describe("PlatformAdapterCard Granular Day 9 Check 27", () => {
  it("renders card for custom platform scenario 27", () => {
    const q: PlatformQuotaStatus = {
      platform: "tiktok",
      daily_quota_limit: 6700,
      quota_used_today: 270,
      quota_remaining: 6430,
      rate_limit_rpm: 100,
      auth_state: "api_configured",
      status: "active",
    };

    render(<PlatformAdapterCard quota={q} />);
    expect(screen.getByTestId(`adapter-card-${q.platform}`)).toBeInTheDocument();
  });
});
