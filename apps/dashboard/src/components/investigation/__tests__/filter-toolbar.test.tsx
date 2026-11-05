import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { FilterToolbar } from "../filter-toolbar";

describe("FilterToolbar component", () => {
  it("renders search bar and filter selects", () => {
    const handleSearch = vi.fn();
    const handleBand = vi.fn();
    const handleSort = vi.fn();

    render(
      <FilterToolbar
        searchQuery="bot"
        onSearchChange={handleSearch}
        bandFilter="all"
        onBandFilterChange={handleBand}
        sortBy="score_desc"
        onSortByChange={handleSort}
      />
    );

    expect(screen.getByPlaceholderText("Search by handle or account ID...")).toHaveValue("bot");
    expect(screen.getByText("All Risk Bands")).toBeInTheDocument();
    expect(screen.getByText("Score: High to Low")).toBeInTheDocument();
  });
});
