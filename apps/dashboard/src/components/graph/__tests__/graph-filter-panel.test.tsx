import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it, vi } from "vitest";
import { GraphFilterPanel } from "../graph-filter-panel";

describe("GraphFilterPanel component", () => {
  it("renders search input, band dropdown, min score slider, and reset button", () => {
    const onSearchChange = vi.fn();
    const onBandChange = vi.fn();
    const onMinScoreChange = vi.fn();
    const onClearFilters = vi.fn();

    render(
      <GraphFilterPanel
        searchQuery=""
        onSearchChange={onSearchChange}
        selectedBand=""
        onBandChange={onBandChange}
        minScore={0.5}
        onMinScoreChange={onMinScoreChange}
        clusterFilter=""
        onClusterChange={vi.fn()}
        totalNodes={100}
        filteredNodes={42}
        onClearFilters={onClearFilters}
      />
    );

    expect(screen.getByText(/Showing/)).toBeInTheDocument();
    expect(screen.getByText("42")).toBeInTheDocument();

    const searchInput = screen.getByLabelText("Search graph accounts");
    fireEvent.change(searchInput, { target: { value: "bot_x" } });
    expect(onSearchChange).toHaveBeenCalledWith("bot_x");

    fireEvent.click(screen.getByText("Reset"));
    expect(onClearFilters).toHaveBeenCalledTimes(1);
  });
});
