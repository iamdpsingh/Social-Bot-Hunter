import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it, vi } from "vitest";
import ErrorBoundary from "../error";

describe("InvestigationGraph Error component", () => {
  it("renders error message and invokes reset callback", () => {
    const reset = vi.fn();
    render(<ErrorBoundary error={new Error("Graph fetch failure")} reset={reset} />);

    expect(screen.getByText("Failed to load network graph")).toBeInTheDocument();
    expect(screen.getByText("Graph fetch failure")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Retry Loading" }));
    expect(reset).toHaveBeenCalledTimes(1);
  });
});
