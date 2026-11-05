"use client";

import useSWR from "swr";
import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";
import type { AccountEvidenceResponse } from "../api/types";

export function useAccountEvidence(scanId: string | null, accountId: string | null) {
  const url = scanId && accountId ? ENDPOINTS.accounts.evidence(scanId, accountId) : null;

  const { data, error, isLoading, mutate } = useSWR<AccountEvidenceResponse>(url, apiClient, {
    revalidateOnFocus: false,
  });

  return {
    evidence: data?.evidence || [],
    total: data?.total || 0,
    isLoading,
    isError: !!error,
    error,
    mutate,
  };
}
