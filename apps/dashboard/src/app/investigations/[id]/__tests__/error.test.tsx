import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import InvestigationDetailError from "../error";

describe("InvestigationDetailError", () => {
  it("renders error message and provides retry and back navigation", () => {
    const handleReset = vi.fn();
    render(<InvestigationDetailError error={new Error("Workspace unavailable")} reset={handleReset} />);

    expect(screen.getByText("Failed to load investigation workspace")).toBeInTheDocument();
    expect(screen.getByText("Workspace unavailable")).toBeInTheDocument();

    fireEvent.click(screen.getByText("Retry"));
    expect(handleReset).toHaveBeenCalledTimes(1);
  });
});
