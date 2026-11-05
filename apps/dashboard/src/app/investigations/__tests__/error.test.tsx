import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import InvestigationsError from "../error";

describe("InvestigationsError", () => {
  it("renders error description and invokes reset on retry button click", () => {
    const handleReset = vi.fn();
    render(<InvestigationsError error={new Error("Network timeout")} reset={handleReset} />);

    expect(screen.getByText("Unable to load investigations")).toBeInTheDocument();
    expect(screen.getByText("Network timeout")).toBeInTheDocument();

    fireEvent.click(screen.getByText("Retry"));
    expect(handleReset).toHaveBeenCalledTimes(1);
  });
});
