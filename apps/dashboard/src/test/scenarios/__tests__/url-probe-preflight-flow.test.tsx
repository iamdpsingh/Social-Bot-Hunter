import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { UrlProbeModal } from "../../../components/adapters/url-probe-modal";

describe("Scenario: URL Probe Preflight Flow", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("completes URL input, validation, and probe target selection", async () => {
    const handleSelectTarget = vi.fn();
    const handleClose = vi.fn();

    // Mock global fetch for validation and probe
    global.fetch = vi.fn().mockImplementation((url: string) => {
      if (url.includes("/adapters/validate-url")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              platform: "youtube",
              handle: "@veritasium",
              canonical_url: "https://www.youtube.com/@veritasium",
              raw_url: "https://youtube.com/@veritasium",
              url_type: "handle",
              is_canonical: true,
            }),
        });
      }
      if (url.includes("/adapters/probe")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              platform: "youtube",
              handle: "@veritasium",
              canonical_url: "https://www.youtube.com/@veritasium",
              outcome: "ok",
              account: {
                platform: "youtube",
                platform_account_id: "UCHnyfMqiRRG1u-2MsSQLbXA",
                display_name: "Veritasium",
                follower_count: 15400000,
                post_count: 390,
              },
              daily_quota_remaining: 9998,
            }),
        });
      }
      return Promise.reject(new Error("Unknown URL"));
    });

    render(
      <UrlProbeModal
        isOpen={true}
        onClose={handleClose}
        onSelectTarget={handleSelectTarget}
      />
    );

    const input = screen.getByLabelText(/Target Account Profile URL or Handle/i);
    fireEvent.change(input, { target: { value: "https://youtube.com/@veritasium" } });

    const submitBtn = screen.getByRole("button", { name: /Probe/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText("Veritasium")).toBeInTheDocument();
      expect(screen.getByText(/15,400,000 Followers/i)).toBeInTheDocument();
    });

    const selectBtn = screen.getByRole("button", { name: /Use Target for Scan/i });
    fireEvent.click(selectBtn);

    expect(handleSelectTarget).toHaveBeenCalledWith("youtube", "@veritasium");
  });
});
