import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { EvidenceInspector } from "../evidence-inspector";

describe("EvidenceInspector component", () => {
  it("renders accordion header and expands signals list", () => {
    const assessment: any = {
      contributions: [
        { signal: "rapid_burst", weight: 0.4, value: 0.85, description: "Unusually high follow velocity" },
      ],
    };
    render(<EvidenceInspector assessment={assessment} />);
    expect(screen.getByText("Contributing Risk Signals & Evidence")).toBeInTheDocument();
    expect(screen.getByText("rapid_burst")).toBeInTheDocument();
    expect(screen.getByText("Unusually high follow velocity")).toBeInTheDocument();

    const toggle = screen.getByLabelText("Toggle Evidence");
    fireEvent.click(toggle);
    expect(screen.queryByText("Unusually high follow velocity")).not.toBeInTheDocument();
  });
});
