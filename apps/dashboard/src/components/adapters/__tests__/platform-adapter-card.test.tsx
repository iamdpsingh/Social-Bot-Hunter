import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { PlatformAdapterCard } from "../platform-adapter-card";
import { PlatformQuotaStatus } from "../../../lib/api/types";

const mockQuota: PlatformQuotaStatus = {
  platform: "youtube",
  daily_quota_limit: 10000,
  quota_used_today: 1500,
  quota_remaining: 8500,
  rate_limit_rpm: 600,
  auth_state: "api_key_configured",
  status: "active",
};

describe("PlatformAdapterCard", () => {
  it("renders platform adapter name, status and rate limit", () => {
    render(<PlatformAdapterCard quota={mockQuota} />);
    expect(screen.getByText(/youtube data api/i)).toBeInTheDocument();
    expect(screen.getByText(/active/i)).toBeInTheDocument();
    expect(screen.getByText(/600 req\/min limit/i)).toBeInTheDocument();
  });
});
