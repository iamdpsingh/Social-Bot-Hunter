import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import AccountDetailError from "../error";

describe("AccountDetailError", () => {
  it("renders error description and retry handler", () => {
    const handleReset = vi.fn();
    render(<AccountDetailError error={new Error("Assessment failure")} reset={handleReset} />);

    expect(screen.getByText("Unable to load account assessment")).toBeInTheDocument();
    expect(screen.getByText("Assessment failure")).toBeInTheDocument();

    fireEvent.click(screen.getByText("Retry Assessment"));
    expect(handleReset).toHaveBeenCalledTimes(1);
  });
});
