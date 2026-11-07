"use client";

import React, { useState } from "react";
import { useScanDiff } from "../../../lib/hooks/use-scan-diff";
import { DiffSelector } from "../../../components/diff/diff-selector";
import { DiffMetricSummary } from "../../../components/diff/diff-metric-summary";
import { CoverageGapBanner } from "../../../components/diff/coverage-gap-banner";
import { DiffAccountTable } from "../../../components/diff/diff-account-table";

export function DiffClient() {
  const [scanAInput, setScanAInput] = useState("");
  const [scanBInput, setScanBInput] = useState("");
  const [activeScanA, setActiveScanA] = useState("");
  const [activeScanB, setActiveScanB] = useState("");

  const { diff, isLoading, isError } = useScanDiff(activeScanA, activeScanB);

  const handleCompare = () => {
    setActiveScanA(scanAInput.trim());
    setActiveScanB(scanBInput.trim());
  };

  return (
    <div data-testid="scan-diff-page" className="space-y-6">
      <div>
        <h2 className="text-2xl font-black text-foreground">Multi-Scan Comparison (Diff)</h2>
        <p className="text-xs text-muted-foreground mt-1">
          Compare two investigation scans side-by-side to track botnet evolutions,
          distinguish proven removals from coverage limits, and observe risk score migrations.
        </p>
      </div>

      <DiffSelector
        scanA={scanAInput}
        scanB={scanBInput}
        onScanAChange={setScanAInput}
        onScanBChange={setScanBInput}
        onCompare={handleCompare}
      />

      {isLoading && (
        <div data-testid="diff-loading" className="p-12 text-center text-sm text-muted-foreground animate-pulse">
          Computing multi-scan differences, edge topologies, and score migrations...
        </div>
      )}

      {isError && (
        <div data-testid="diff-error" className="p-6 text-center rounded-xl border border-destructive/30 bg-destructive/10 text-destructive text-sm font-semibold">
          Failed to compute diff between the specified scans. Please verify scan IDs exist.
        </div>
      )}

      {diff && (
        <div className="space-y-6">
          <DiffMetricSummary diff={diff} />

          {(diff.coverage_gap_additions_count > 0 || diff.coverage_gap_removals_count > 0) && (
            <CoverageGapBanner
              coverageGapsCount={diff.coverage_gap_additions_count + diff.coverage_gap_removals_count}
            />
          )}

          <DiffAccountTable accounts={diff.accounts} />
        </div>
      )}
    </div>
  );
}
