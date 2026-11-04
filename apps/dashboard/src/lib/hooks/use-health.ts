"use client";

import useSWR from "swr";
import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";
import type { HealthResponse } from "../api/types";

export function useHealth(refreshInterval = 10000) {
  const { data, error, isLoading, mutate } = useSWR<HealthResponse>(
    ENDPOINTS.health,
    apiClient,
    {
      refreshInterval,
      revalidateOnFocus: true,
      dedupingInterval: 5000,
    }
  );

  return {
    health: data,
    isLoading,
    isError: !!error,
    error,
    mutate,
  };
}
