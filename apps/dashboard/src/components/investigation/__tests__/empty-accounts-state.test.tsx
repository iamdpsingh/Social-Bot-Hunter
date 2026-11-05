import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { EmptyAccountsState } from "../empty-accounts-state";

describe("EmptyAccountsState component", () => {
  it("renders empty state notice and handles reset action", () => {
    const handleReset = vi.fn();
    render(<EmptyAccountsState onResetFilters={handleReset} />);
    expect(screen.getByText("No accounts match query")).toBeInTheDocument();
    const btn = screen.getByText("Reset Search Filters");
    fireEvent.click(btn);
    expect(handleReset).toHaveBeenCalled();
  });
});
