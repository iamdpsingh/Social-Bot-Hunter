"use client";

import React from "react";

interface DiffSelectorProps {
  scanA: string;
  scanB: string;
  onScanAChange: (val: string) => void;
  onScanBChange: (val: string) => void;
  onCompare: () => void;
}

export function DiffSelector({
  scanA,
  scanB,
  onScanAChange,
  onScanBChange,
  onCompare,
}: DiffSelectorProps) {
  return (
    <div
      data-testid="diff-selector"
      className="p-5 rounded-xl border border-border bg-card shadow-sm flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4"
    >
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 flex-1">
        <label className="flex-1 text-xs font-semibold text-muted-foreground flex flex-col gap-1.5">
          <span>Baseline Scan (Earlier / Scan A):</span>
          <input
            type="text"
            data-testid="input-scan-a"
            placeholder="Enter scan ID A (e.g. scan_baseline_01)"
            value={scanA}
            onChange={(e) => onScanAChange(e.target.value)}
            className="px-3 py-2 text-xs rounded-lg border border-border bg-background text-foreground font-mono focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </label>

        <div className="hidden sm:flex items-center text-muted-foreground font-bold text-xs pt-5">
          &rarr;
        </div>

        <label className="flex-1 text-xs font-semibold text-muted-foreground flex flex-col gap-1.5">
          <span>Comparison Scan (Later / Scan B):</span>
          <input
            type="text"
            data-testid="input-scan-b"
            placeholder="Enter scan ID B (e.g. scan_followup_02)"
            value={scanB}
            onChange={(e) => onScanBChange(e.target.value)}
            className="px-3 py-2 text-xs rounded-lg border border-border bg-background text-foreground font-mono focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </label>
      </div>

      <button
        type="button"
        data-testid="btn-compare-scans"
        onClick={onCompare}
        disabled={!scanA || !scanB}
        className="px-5 py-2.5 rounded-lg bg-primary text-primary-foreground font-semibold text-xs shadow hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors self-end md:self-center"
      >
        Compare Scans
      </button>
    </div>
  );
}
