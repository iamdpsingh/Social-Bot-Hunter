import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { RetentionConfigCard } from "../retention-config-card";

describe("RetentionConfigCard", () => {
  const mockStats = {
    total_scans: 25,
    oldest_scan_at: "2026-08-01",
    retention_days: 90,
    expired_scans_count: 5,
    database_size_bytes: 204800,
    auto_purge_enabled: true,
  };

  it("triggers dry run and purge handlers", async () => {
    const onPurge = vi.fn().mockResolvedValue(undefined);
    render(<RetentionConfigCard stats={mockStats} onPurge={onPurge} />);
    expect(screen.getByText("25")).toBeInTheDocument();

    const dryRunBtn = screen.getByTestId("btn-dry-run-purge");
    fireEvent.click(dryRunBtn);
    expect(onPurge).toHaveBeenCalledWith(90, true);
  });
});
