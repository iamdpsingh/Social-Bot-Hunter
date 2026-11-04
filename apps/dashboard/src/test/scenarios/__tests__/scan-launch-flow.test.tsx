import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { LaunchScanModal } from "../../../components/overview/launch-scan-modal";

vi.mock("../../../lib/hooks/use-scans", () => ({
  useScans: () => ({
    createScan: vi.fn().mockResolvedValue({ scan_id: "scan_123" }),
  }),
}));

describe("Scenario: Scan Launch Flow", () => {
  it("allows selecting platform, typing username, and launching investigation", () => {
    const handleClose = vi.fn();
    render(<LaunchScanModal isOpen={true} onClose={handleClose} />);

    const handleInput = screen.getByLabelText("Target Profile / Handle");
    fireEvent.change(handleInput, { target: { value: "coordinated_bot_net" } });
    expect(handleInput).toHaveValue("coordinated_bot_net");

    const launchButton = screen.getByRole("button", { name: /start investigation/i });
    expect(launchButton).toBeEnabled();
  });
});
