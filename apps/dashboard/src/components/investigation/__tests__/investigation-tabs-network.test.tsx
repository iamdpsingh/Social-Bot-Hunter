import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it, vi } from "vitest";
import { InvestigationTabs } from "../investigation-tabs";

describe("InvestigationTabs Network Explorer tab", () => {
  it("renders Interactive Network Explorer tab and dispatches onTabChange", () => {
    const onTabChange = vi.fn();
    render(<InvestigationTabs activeTab="overview" onTabChange={onTabChange} />);

    const networkTab = screen.getByRole("tab", { name: /Interactive Network Explorer/ });
    expect(networkTab).toBeInTheDocument();

    fireEvent.click(networkTab);
    expect(onTabChange).toHaveBeenCalledWith("network");
  });
});
