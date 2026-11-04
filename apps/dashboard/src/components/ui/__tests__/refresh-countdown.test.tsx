import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { RefreshCountdown } from "../refresh-countdown";

describe("RefreshCountdown component", () => {
  it("displays remaining seconds and trigger manual refresh", () => {
    const handleRefresh = vi.fn();
    render(<RefreshCountdown secondsRemaining={15} onRefresh={handleRefresh} />);
    expect(screen.getByText("Auto-refreshes in 15s")).toBeInTheDocument();
    const btn = screen.getByLabelText("Refresh now");
    fireEvent.click(btn);
    expect(handleRefresh).toHaveBeenCalled();
  });
});
