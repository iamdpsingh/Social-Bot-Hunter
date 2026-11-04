import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Header } from "../header";

vi.mock("../../../lib/hooks/use-health", () => ({
  useHealth: () => ({
    health: { status: "ok", version: "0.1.0", database: "connected" },
    isLoading: false,
    error: null,
  }),
}));

describe("Header component", () => {
  it("renders platform title and live database indicator", () => {
    render(<Header />);
    expect(screen.getByText("Social Bot Hunter")).toBeInTheDocument();
    expect(screen.getByText("Postgres/SQLite Live")).toBeInTheDocument();
  });

  it("fires new scan callback on action button click", () => {
    const handleNewScan = vi.fn();
    render(<Header onNewScanClick={handleNewScan} />);
    const btn = screen.getByText("New Investigation");
    fireEvent.click(btn);
    expect(handleNewScan).toHaveBeenCalled();
  });
});
