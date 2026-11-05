"use client";

import useSWR from "swr";
import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";
import type { AccountNeighborhoodResponse } from "../api/types";

export function useAccountNeighborhood(scanId: string | null, accountId: string | null) {
  const url = scanId && accountId ? ENDPOINTS.accounts.neighborhood(scanId, accountId) : null;

  const { data, error, isLoading, mutate } = useSWR<AccountNeighborhoodResponse>(url, apiClient, {
    revalidateOnFocus: false,
  });

  return {
    inEdges: data?.in_edges || [],
    outEdges: data?.out_edges || [],
    totalIn: data?.total_in || 0,
    totalOut: data?.total_out || 0,
    isLoading,
    isError: !!error,
    error,
    mutate,
  };
}
