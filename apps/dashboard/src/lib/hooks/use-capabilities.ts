"use client";

import useSWR from "swr";
import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";
import type { CapabilitiesResponse } from "../api/types";

export function useCapabilities() {
  const { data, error, isLoading, mutate } = useSWR<CapabilitiesResponse>(
    ENDPOINTS.capabilities,
    apiClient,
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000,
    }
  );

  return {
    capabilities: data?.capabilities || [],
    total: data?.total || 0,
    isLoading,
    isError: !!error,
    error,
    mutate,
  };
}
