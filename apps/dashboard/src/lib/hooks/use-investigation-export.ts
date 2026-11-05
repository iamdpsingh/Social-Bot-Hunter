"use client";

import { useState } from "react";
import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";

export function useInvestigationExport(scanId: string) {
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const downloadCsv = async (filename?: string) => {
    setIsExporting(true);
    setError(null);
    try {
      const csvText = await apiClient<string>(ENDPOINTS.scans.exportCsv(scanId));
      const blob = new Blob([csvText], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename || `scan_${scanId}_accounts.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Export failed"));
    } finally {
      setIsExporting(false);
    }
  };

  const downloadJson = async (filename?: string) => {
    setIsExporting(true);
    setError(null);
    try {
      const jsonData = await apiClient<Record<string, unknown>>(ENDPOINTS.scans.exportJson(scanId));
      const blob = new Blob([JSON.stringify(jsonData, null, 2)], {
        type: "application/json;charset=utf-8;",
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename || `scan_${scanId}_bundle.json`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Export failed"));
    } finally {
      setIsExporting(false);
    }
  };

  return {
    downloadCsv,
    downloadJson,
    isExporting,
    error,
  };
}
