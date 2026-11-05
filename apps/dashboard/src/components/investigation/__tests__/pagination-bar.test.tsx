import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { PaginationBar } from "../pagination-bar";

describe("PaginationBar component", () => {
  it("renders item ranges and triggers page transitions", () => {
    const handlePage = vi.fn();
    render(
      <PaginationBar
        total={120}
        limit={50}
        offset={0}
        onPageChange={handlePage}
      />
    );

    expect(screen.getByText(/Showing/)).toBeInTheDocument();
    expect(screen.getByText("1 / 3")).toBeInTheDocument();

    const nextBtn = screen.getByLabelText("Next page");
    fireEvent.click(nextBtn);
    expect(handlePage).toHaveBeenCalledWith(50);
  });
});
