import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { SearchBar } from "../search-bar";

describe("SearchBar component", () => {
  it("renders search input with placeholder", () => {
    render(<SearchBar placeholder="Filter targets..." />);
    expect(screen.getByPlaceholderText("Filter targets...")).toBeInTheDocument();
  });

  it("calls onClear when clear button is clicked", () => {
    const handleClear = vi.fn();
    render(<SearchBar value="elon" onClear={handleClear} onChange={() => {}} />);
    const clearBtn = screen.getByLabelText("Clear search");
    fireEvent.click(clearBtn);
    expect(handleClear).toHaveBeenCalled();
  });
});
