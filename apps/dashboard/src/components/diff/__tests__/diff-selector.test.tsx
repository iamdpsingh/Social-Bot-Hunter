import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { DiffSelector } from "../diff-selector";

describe("DiffSelector", () => {
  it("triggers onCompare when valid IDs provided", () => {
    const onCompare = vi.fn();
    render(
      <DiffSelector
        scanA="scan_1"
        scanB="scan_2"
        onScanAChange={vi.fn()}
        onScanBChange={vi.fn()}
        onCompare={onCompare}
      />
    );
    const btn = screen.getByTestId("btn-compare-scans");
    expect(btn).not.toBeDisabled();
    fireEvent.click(btn);
    expect(onCompare).toHaveBeenCalled();
  });
});
