import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { LaunchScanModal } from "../launch-scan-modal";

vi.mock("../../../lib/hooks/use-scans", () => ({
  useScans: () => ({
    createScan: vi.fn().mockResolvedValue({ scan_id: "scan_123" }),
  }),
}));

describe("LaunchScanModal component", () => {
  it("renders modal form inputs and handles cancel", () => {
    const handleClose = vi.fn();
    render(<LaunchScanModal isOpen={true} onClose={handleClose} />);
    expect(screen.getByLabelText("Social Media Platform")).toBeInTheDocument();
    expect(screen.getByLabelText("Target Profile / Handle")).toBeInTheDocument();
    const cancelBtn = screen.getByText("Cancel");
    fireEvent.click(cancelBtn);
    expect(handleClose).toHaveBeenCalled();
  });
});
