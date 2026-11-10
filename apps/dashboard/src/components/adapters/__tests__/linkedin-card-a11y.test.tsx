import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { PlatformAdapterCard } from "../platform-adapter-card";
import { PlatformQuotaStatus } from "../../../lib/api/types";

describe("PlatformAdapterCard A11y", () => {
  it("has accessible label for screen readers", () => {
    const quota: PlatformQuotaStatus = {
      platform: "linkedin",
      daily_quota_limit: 2500,
      quota_used_today: 100,
      quota_remaining: 2400,
      rate_limit_rpm: 100,
      auth_state: "configured",
      status: "active",
    };
    render(<PlatformAdapterCard quota={quota} />);
    const card = screen.getByRole("generic", { name: /linkedin platform adapter status/i });
    expect(card).toBeInTheDocument();
  });
});
