"use client";

import useSWR from "swr";
import { getScanCoordinationEndpoint } from "../api/endpoints";
import { fetcher } from "../api/fetcher";
import type { CoordinationSummaryResponse } from "../api/types";

export function useCoordination(
  scanId: string,
  burstWindowSeconds: number = 60,
  minSimilarityDistance: number = 4
) {
  const endpoint = scanId
    ? getScanCoordinationEndpoint(scanId, burstWindowSeconds, minSimilarityDistance)
    : null;

  const { data, error, isLoading, mutate } = useSWR<CoordinationSummaryResponse>(
    endpoint,
    fetcher,
    {
      revalidateOnFocus: false,
      dedupingInterval: 10000,
    }
  );

  return {
    coordination: data,
    isLoading,
    isError: !!error,
    error,
    mutate,
  };
}
