import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { EmptyInvestigationState } from "../empty-investigation-state";

describe("EmptyInvestigationState component", () => {
  it("renders zero state message and invokes new scan handler", () => {
    const handleNewScan = vi.fn();
    render(<EmptyInvestigationState onNewScanClick={handleNewScan} />);
    expect(screen.getByText("No investigations launched yet")).toBeInTheDocument();
    const btn = screen.getByText("Launch Your First Scan");
    fireEvent.click(btn);
    expect(handleNewScan).toHaveBeenCalled();
  });
});
