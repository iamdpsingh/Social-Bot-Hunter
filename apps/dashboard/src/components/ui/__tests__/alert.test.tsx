import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Alert } from "../alert";

describe("Alert component", () => {
  it("renders with default info variant", () => {
    render(<Alert title="System Note">Database backup running in background</Alert>);
    expect(screen.getByRole("alert")).toBeInTheDocument();
    expect(screen.getByText("System Note")).toBeInTheDocument();
    expect(screen.getByText("Database backup running in background")).toBeInTheDocument();
  });

  it("renders destructive variant for errors", () => {
    render(<Alert variant="destructive" title="Scan Failed">Target account not accessible</Alert>);
    const alert = screen.getByRole("alert");
    expect(alert).toHaveClass("border-red-500/20");
    expect(screen.getByText("Scan Failed")).toBeInTheDocument();
  });

  it("renders warning and success variants", () => {
    const { rerender } = render(<Alert variant="warning">Rate limit warning</Alert>);
    expect(screen.getByRole("alert")).toHaveClass("border-amber-500/20");

    rerender(<Alert variant="success">Scan completed</Alert>);
    expect(screen.getByRole("alert")).toHaveClass("border-emerald-500/20");
  });
});
