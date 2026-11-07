import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { PlatformCapabilityCard } from "../../../components/settings/platform-capability-card";

describe("PlatformCapabilityCard Accessibility", () => {
  it("provides accessible tabular layout for platform quotas", () => {
    render(<PlatformCapabilityCard quotas={[]} />);
    expect(screen.getByRole("table")).toBeInTheDocument();
    expect(screen.getAllByRole("columnheader").length).toBe(5);
  });
});
