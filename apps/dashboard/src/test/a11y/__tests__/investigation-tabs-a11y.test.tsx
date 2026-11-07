import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { InvestigationTabs } from "../../../components/investigation/investigation-tabs";

describe("InvestigationTabs Accessibility", () => {
  it("provides tablist role, tab roles, and aria-selected state", () => {
    const handleChange = vi.fn();
    render(<InvestigationTabs activeTab="overview" onTabChange={handleChange} />);

    const tablist = screen.getByRole("tablist");
    expect(tablist).toBeInTheDocument();

    const tabs = screen.getAllByRole("tab");
    expect(tabs.length).toBe(6);

    const activeTab = screen.getByRole("tab", { name: /Overview/ });
    expect(activeTab).toHaveAttribute("aria-selected", "true");

    const explorerTab = screen.getByRole("tab", { name: /Followers/ });
    expect(explorerTab).toHaveAttribute("aria-selected", "false");
  });
});
