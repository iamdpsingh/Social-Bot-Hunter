import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { EmptyInvestigationState } from "../empty-investigation-state";

describe("EmptyInvestigationState component", () => {
  it("renders zero state message and invokes action handler", () => {
    const handleAction = vi.fn();
    render(<EmptyInvestigationState onActionClick={handleAction} />);
    expect(screen.getByText("No Active Investigations")).toBeInTheDocument();
    const btn = screen.getByText("Start Scan");
    fireEvent.click(btn);
    expect(handleAction).toHaveBeenCalled();
  });
});
