"use client";

import useSWR from "swr";
import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";
import type { AuditListResponse } from "../api/types";

export function useAudit(limit = 15) {
  const url = `${ENDPOINTS.audit}?limit=${limit}`;
  const { data, error, isLoading, mutate } = useSWR<AuditListResponse>(url, apiClient, {
    refreshInterval: 10000,
    revalidateOnFocus: true,
  });

  return {
    events: data?.events || [],
    total: data?.total || 0,
    isLoading,
    isError: !!error,
    error,
    mutate,
  };
}
