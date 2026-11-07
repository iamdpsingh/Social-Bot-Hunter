import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { DiffAccountTable } from "../../../components/diff/diff-account-table";

describe("DiffAccountTable Accessibility", () => {
  it("provides accessible table headers and filter buttons", () => {
    render(<DiffAccountTable accounts={[]} />);
    expect(screen.getByRole("table")).toBeInTheDocument();
    expect(screen.getAllByRole("columnheader").length).toBe(5);
    expect(screen.getByPlaceholderText("Filter by handle or ID...")).toHaveAttribute("type", "text");
  });
});
