"use client";

import useSWR from "swr";
import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";
import type { CreateScanPayload, ScanDetailResponse, ScanJob, ScanListResponse } from "../api/types";

export function useScans(limit = 20) {
  const url = `${ENDPOINTS.scans.list}?limit=${limit}`;
  const { data, error, isLoading, mutate } = useSWR<ScanListResponse>(url, apiClient, {
    refreshInterval: 15000,
    revalidateOnFocus: true,
  });

  const createScan = async (payload: CreateScanPayload): Promise<{ scan_id: string }> => {
    const res = await apiClient<{ scan_id: string }>(ENDPOINTS.scans.create, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    await mutate();
    return res;
  };

  const cancelScan = async (id: string): Promise<void> => {
    await apiClient(ENDPOINTS.scans.cancel(id), { method: "POST" });
    await mutate();
  };

  const retryScan = async (id: string): Promise<void> => {
    await apiClient(ENDPOINTS.scans.retry(id), { method: "POST" });
    await mutate();
  };

  return {
    scans: data?.scans || [],
    total: data?.total || 0,
    isLoading,
    isError: !!error,
    error,
    mutate,
    createScan,
    cancelScan,
    retryScan,
  };
}

export function useScan(scanId: string | null) {
  const url = scanId ? ENDPOINTS.scans.get(scanId) : null;
  const { data, error, isLoading, mutate } = useSWR<ScanDetailResponse>(url, apiClient, {
    refreshInterval: 5000,
  });

  return {
    scan: data?.scan as ScanJob | undefined,
    isLoading,
    isError: !!error,
    error,
    mutate,
  };
}
