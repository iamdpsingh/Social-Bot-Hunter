"use client";

import useSWR from "swr";
import { endpoints } from "../api/endpoints";
import { fetcher } from "../api/client";
import { AdapterTelemetryResponse } from "../api/types";

export function useAdapterTelemetry() {
  const { data, error, isLoading, mutate } = useSWR<AdapterTelemetryResponse>(
    endpoints.adapterTelemetry(),
    fetcher,
    { refreshInterval: 10000, revalidateOnFocus: true }
  );

  return {
    telemetry: data?.telemetry || [],
    isLoading,
    isError: !!error,
    error,
    mutate,
  };
}
