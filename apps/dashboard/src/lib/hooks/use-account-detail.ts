"use client";

import useSWR from "swr";
import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";
import type { AccountDetailResponse } from "../api/types";

export function useAccountDetail(scanId: string | null, accountId: string | null) {
  const url = scanId && accountId ? ENDPOINTS.accounts.detail(scanId, accountId) : null;

  const { data, error, isLoading, mutate } = useSWR<AccountDetailResponse>(url, apiClient, {
    revalidateOnFocus: false,
  });

  return {
    assessment: data?.assessment,
    observation: data?.profile_observation,
    features: data?.features || [],
    isLoading,
    isError: !!error,
    error,
    mutate,
  };
}
