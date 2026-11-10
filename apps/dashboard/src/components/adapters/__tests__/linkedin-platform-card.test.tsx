import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { PlatformAdapterCard } from "../platform-adapter-card";
import { PlatformQuotaStatus } from "../../../lib/api/types";

const mockLinkedInQuota: PlatformQuotaStatus = {
  platform: "linkedin",
  daily_quota_limit: 2500,
  quota_used_today: 450,
  quota_remaining: 2050,
  rate_limit_rpm: 100,
  auth_state: "oauth2_app_configured",
  status: "active",
};

describe("LinkedIn PlatformAdapterCard", () => {
  it("renders linkedin data api name, subtitle and active status", () => {
    render(<PlatformAdapterCard quota={mockLinkedInQuota} />);
    expect(screen.getByText(/linkedin data api/i)).toBeInTheDocument();
    expect(screen.getByText(/community management api v2/i)).toBeInTheDocument();
    expect(screen.getByText(/active/i)).toBeInTheDocument();
  });
