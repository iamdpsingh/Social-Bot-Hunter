import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { InvestigationTabs } from "../investigation-tabs";

describe("InvestigationTabs component", () => {
  it("renders tab labels and invokes onTabChange on tab click", () => {
    const handleChange = vi.fn();
    render(<InvestigationTabs activeTab="overview" onTabChange={handleChange} />);
    expect(screen.getByText("Overview & Evidence")).toBeInTheDocument();
    expect(screen.getByText("Followers & Following Explorer")).toBeInTheDocument();

    const explorerTab = screen.getByText("Followers & Following Explorer");
    fireEvent.click(explorerTab);
    expect(handleChange).toHaveBeenCalledWith("explorer");
  });
});
