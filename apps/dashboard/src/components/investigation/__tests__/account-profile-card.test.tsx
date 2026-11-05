import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { AccountProfileCard } from "../account-profile-card";

describe("AccountProfileCard component", () => {
  it("renders username, follower counts, and bio", () => {
    render(
      <AccountProfileCard
        accountId="acc_99"
        observation={{
          id: "obs_1",
          platform_account_id: "acc_99",
          username: "target_account",
          display_name: "Target Profile",
          bio: "Automated network test runner account",
          followers_count: 500,
          following_count: 1200,
          posts_count: 42,
          observed_at: "2026-11-05T09:00:00Z",
        }}
      />
    );

    expect(screen.getByText("Target Profile")).toBeInTheDocument();
    expect(screen.getByText("@target_account")).toBeInTheDocument();
    expect(screen.getByText("500")).toBeInTheDocument();
    expect(screen.getByText("1,200")).toBeInTheDocument();
    expect(screen.getByText(/Automated network test/)).toBeInTheDocument();
  });
});
