import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { FilterToolbar } from "../../../components/investigation/filter-toolbar";

describe("Scenario: Follower Explorer Filtering", () => {
  it("updates search query and risk band filters interactively", () => {
    const handleSearch = vi.fn();
    const handleBand = vi.fn();

    render(
      <FilterToolbar
        search=""
        onSearchChange={handleSearch}
        riskBand="all"
        onRiskBandChange={handleBand}
      />
    );

    const input = screen.getByPlaceholderText(/Search by handle/);
    fireEvent.change(input, { target: { value: "suspicious_bot" } });
    expect(handleSearch).toHaveBeenCalledWith("suspicious_bot");

    const selects = screen.getAllByRole("combobox");
    fireEvent.change(selects[0], { target: { value: "critical" } });
    expect(handleBand).toHaveBeenCalledWith("critical");
  });
});
