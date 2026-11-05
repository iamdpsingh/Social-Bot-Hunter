import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { EvidenceItemRow } from "../evidence-item-row";

describe("EvidenceItemRow component", () => {
  it("renders signal name, weight tag, and description", () => {
    render(
      <EvidenceItemRow
        signal={{
          signal: "default_avatar",
          weight: 0.25,
          value: 1.0,
          description: "Account has not uploaded a custom profile picture",
        }}
      />
    );
    expect(screen.getByText("default_avatar")).toBeInTheDocument();
    expect(screen.getByText("Weight: 25%")).toBeInTheDocument();
    expect(screen.getByText("Account has not uploaded a custom profile picture")).toBeInTheDocument();
  });
});
