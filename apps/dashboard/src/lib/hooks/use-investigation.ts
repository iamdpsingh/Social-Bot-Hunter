"use client";

import useSWR from "swr";
import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";
import type { ScanReportResponse, ScanDetailResponse, ScanJob } from "../api/types";

export function useInvestigation(scanId: string | null) {
  const scanUrl = scanId ? ENDPOINTS.scans.get(scanId) : null;
  const reportUrl = scanId ? ENDPOINTS.scans.report(scanId) : null;

  const {
    data: scanData,
    error: scanError,
    isLoading: isScanLoading,
  } = useSWR<ScanDetailResponse>(scanUrl, apiClient);

  const {
    data: reportData,
    error: reportError,
    isLoading: isReportLoading,
    mutate: mutateReport,
  } = useSWR<ScanReportResponse>(reportUrl, apiClient, {
    revalidateOnFocus: true,
  });

  return {
    scan: scanData?.scan as ScanJob | undefined,
    report: reportData,
    isLoading: isScanLoading || isReportLoading,
    isError: !!scanError || !!reportError,
    error: scanError || reportError,
    refresh: mutateReport,
  };
}
