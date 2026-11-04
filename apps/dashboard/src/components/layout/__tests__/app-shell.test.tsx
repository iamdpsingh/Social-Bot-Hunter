import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { AppShell } from "../app-shell";

vi.mock("../../../lib/hooks/use-health", () => ({
  useHealth: () => ({
    health: { status: "ok", version: "0.1.0", database: "connected" },
    isLoading: false,
  }),
}));

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
}));

describe("AppShell component", () => {
  it("renders shell wrapper with children in main content area", () => {
    render(
      <AppShell>
        <div data-testid="dashboard-content">Command Center Feed</div>
      </AppShell>
    );

    expect(screen.getByTestId("dashboard-content")).toBeInTheDocument();
    expect(screen.getByText("Social Bot Hunter")).toBeInTheDocument();
  });
});
