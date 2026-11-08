"use client";

import useSWR from "swr";
import { endpoints } from "../api/endpoints";
import { fetcher } from "../api/client";
import { PlatformQuotaStatus } from "../api/types";

export function useAdapterQuotas() {
  const { data, error, isLoading, mutate } = useSWR<PlatformQuotaStatus[]>(
    endpoints.adapterQuotas(),
    fetcher,
    { refreshInterval: 15000, revalidateOnFocus: true }
  );

  return {
    quotas: data || [],
    isLoading,
    isError: !!error,
    error,
    mutate,
  };
}
