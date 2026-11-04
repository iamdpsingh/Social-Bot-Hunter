import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { Sidebar } from "../sidebar";

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
}));

describe("Sidebar component", () => {
  it("renders navigation links and provenance reminder", () => {
    render(<Sidebar />);
    expect(screen.getByText("Overview")).toBeInTheDocument();
    expect(screen.getByText("Investigations")).toBeInTheDocument();
    expect(screen.getByText("Network Explorer")).toBeInTheDocument();
    expect(screen.getByText("OpenAPI Specification")).toBeInTheDocument();
    expect(screen.getByText("Provenance & Safety")).toBeInTheDocument();
  });
});
