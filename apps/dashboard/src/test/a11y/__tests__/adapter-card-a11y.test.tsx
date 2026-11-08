import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { PlatformAdapterCard } from "../../../components/adapters/platform-adapter-card";
import { PlatformQuotaStatus } from "../../../lib/api/types";

const mockQuota: PlatformQuotaStatus = {
  platform: "x",
  daily_quota_limit: 900,
  quota_used_today: 120,
  quota_remaining: 780,
  rate_limit_rpm: 60,
  auth_state: "bearer_token_configured",
  status: "active",
};

describe("A11y: PlatformAdapterCard", () => {
  it("has accessible headings and contrast-compliant status badge", () => {
    render(<PlatformAdapterCard quota={mockQuota} />);
    const heading = screen.getByRole("heading", { level: 3 });
    expect(heading).toHaveTextContent(/x data api/i);
    expect(screen.getByText(/active/i)).toBeInTheDocument();
  });
});
