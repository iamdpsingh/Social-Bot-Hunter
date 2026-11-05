"use client";

import useSWR from "swr";
import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";
import type { AccountAssessment, AccountFilterParams } from "../api/types";

interface AccountListApiResponse {
  scan_id: string;
  total: number;
  offset: number;
  limit: number;
  accounts: AccountAssessment[];
}

export function useAccounts(scanId: string | null, params?: AccountFilterParams) {
  const queryParams = new URLSearchParams();
  if (params?.limit) queryParams.set("limit", String(params.limit));
  if (params?.offset) queryParams.set("offset", String(params.offset));
  if (params?.band) queryParams.set("band", params.band);
  if (params?.status) queryParams.set("status", params.status);
  if (params?.search) queryParams.set("search", params.search);
  if (params?.sort_by) queryParams.set("sort_by", params.sort_by);

  const qs = queryParams.toString();
  const url = scanId ? `${ENDPOINTS.accounts.list(scanId)}${qs ? `?${qs}` : ""}` : null;

  const { data, error, isLoading, mutate } = useSWR<AccountListApiResponse>(url, apiClient, {
    revalidateOnFocus: false,
    dedupingInterval: 5000,
  });

  return {
    accounts: data?.accounts || [],
    total: data?.total || 0,
    offset: data?.offset || 0,
    limit: data?.limit || params?.limit || 50,
    isLoading,
    isError: !!error,
    error,
    mutate,
  };
}
