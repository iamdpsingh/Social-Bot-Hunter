import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { EmptyAccountsState } from "../../../components/investigation/empty-accounts-state";

describe("Scenario: Empty Accounts Filter Reset Flow", () => {
  it("invokes reset filters callback on button click", () => {
    const handleReset = vi.fn();
    render(<EmptyAccountsState onResetFilters={handleReset} />);

    expect(screen.getByText("No accounts match query")).toBeInTheDocument();
    const btn = screen.getByText("Reset Search Filters");
    fireEvent.click(btn);
    expect(handleReset).toHaveBeenCalledTimes(1);
  });
});
