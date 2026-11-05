import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import InvestigationDetailError from "../../../app/investigations/[id]/error";

describe("Scenario: Network Error Resilience", () => {
  it("renders error recovery CTA when investigation workspace fetch fails", () => {
    const handleRetry = vi.fn();
    render(
      <InvestigationDetailError
        error={new Error("Database connection terminated prematurely")}
        reset={handleRetry}
      />
    );

    expect(screen.getByText("Failed to load investigation workspace")).toBeInTheDocument();
    expect(screen.getByText("Database connection terminated prematurely")).toBeInTheDocument();

    const retryBtn = screen.getByRole("button", { name: /Retry/i });
    fireEvent.click(retryBtn);
    expect(handleRetry).toHaveBeenCalledTimes(1);
  });
});
