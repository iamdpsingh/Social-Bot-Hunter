"use client";

import React, { useState } from "react";
import { Download, FileSpreadsheet, FileCode, CheckCircle2, AlertCircle } from "lucide-react";
import { Button } from "../ui/button";

export interface ExportPanelProps {
  scanId: string;
  onExportCsv?: () => void;
  onExportJson?: () => void;
  isExporting?: boolean;
}

export function ExportPanel({ scanId, onExportCsv, onExportJson, isExporting = false }: ExportPanelProps) {
  const [selectedFormat, setSelectedFormat] = useState<"csv" | "json">("csv");
  const [exportComplete, setExportComplete] = useState<string | null>(null);

  const handleTrigger = () => {
    if (selectedFormat === "csv") {
      onExportCsv?.();
      setExportComplete("CSV export initiated for scan " + scanId);
    } else {
      onExportJson?.();
      setExportComplete("JSON export bundle initiated for scan " + scanId);
    }
  };

  return (
    <div className="rounded-lg border border-border bg-card p-6 space-y-5" data-testid="export-panel">
      <div>
        <h3 className="text-base font-semibold text-foreground flex items-center gap-2">
          <Download className="h-4 w-4 text-primary" />
          Investigation Data Export
        </h3>
        <p className="text-xs text-muted-foreground mt-1">
          Download complete investigation records, account risk evaluations, and evidence provenance for audit compliance.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <button
          type="button"
          onClick={() => setSelectedFormat("csv")}
          className={`flex items-start gap-3 p-4 rounded-lg border text-left transition-all ${
            selectedFormat === "csv"
              ? "border-primary bg-primary/5 ring-1 ring-primary"
              : "border-border bg-muted/20 hover:border-border/80"
          }`}
        >
          <FileSpreadsheet className="h-5 w-5 text-emerald-500 mt-0.5" />
          <div>
            <div className="text-sm font-medium text-foreground">CSV Spreadsheet</div>
            <div className="text-xs text-muted-foreground mt-0.5">Tabular rows with risk scores and key metrics</div>
          </div>
        </button>

        <button
          type="button"
          onClick={() => setSelectedFormat("json")}
          className={`flex items-start gap-3 p-4 rounded-lg border text-left transition-all ${
            selectedFormat === "json"
              ? "border-primary bg-primary/5 ring-1 ring-primary"
              : "border-border bg-muted/20 hover:border-border/80"
          }`}
        >
          <FileCode className="h-5 w-5 text-primary mt-0.5" />
          <div>
            <div className="text-sm font-medium text-foreground">JSON Bundle</div>
            <div className="text-xs text-muted-foreground mt-0.5">Full schema with nested evidence and rule trace</div>
          </div>
        </button>
      </div>

      {exportComplete && (
        <div className="flex items-center gap-2 text-xs text-emerald-500 bg-emerald-500/10 p-3 rounded border border-emerald-500/20">
          <CheckCircle2 className="h-4 w-4 shrink-0" />
          <span>{exportComplete}</span>
        </div>
      )}

      <div className="flex justify-end">
        <Button onClick={handleTrigger} disabled={isExporting} className="gap-2">
          <Download className="h-4 w-4" />
          {isExporting ? "Preparing Download..." : `Download ${selectedFormat.toUpperCase()}`}
        </Button>
      </div>
    </div>
  );
}
