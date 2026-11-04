import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import ErrorBoundary from "../error";

describe("Error boundary page", () => {
  it("renders error message and reset button", () => {
    const handleReset = vi.fn();
    render(<ErrorBoundary error={new Error("Failed to load dashboard")} reset={handleReset} />);
    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
    expect(screen.getByText("Failed to load dashboard")).toBeInTheDocument();
    const btn = screen.getByText("Try again");
    fireEvent.click(btn);
    expect(handleReset).toHaveBeenCalled();
  });
});
