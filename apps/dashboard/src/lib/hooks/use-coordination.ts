import { useEffect, useState } from "react";
import { getScanCoordinationEndpoint } from "../api/endpoints";
import type { CoordinationSummaryResponse } from "../api/types";

export function useCoordination(
  scanId: string,
  burstWindowSeconds: number = 60,
  minSimilarityDistance: number = 4
) {
  const [coordination, setCoordination] = useState<CoordinationSummaryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchCoordination = async () => {
    if (!scanId) return;
    try {
      setIsLoading(true);
      setError(null);
      const url = getScanCoordinationEndpoint(scanId, burstWindowSeconds, minSimilarityDistance);
      const res = await fetch(url);
      if (!res.ok) {
        throw new Error(`Failed to load coordination analysis: ${res.statusText}`);
      }
      const json = await res.json();
      setCoordination(json);
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCoordination();
  }, [scanId, burstWindowSeconds, minSimilarityDistance]);

  return {
    coordination,
    isLoading,
    isError: !!error,
    error,
    mutate: fetchCoordination,
  };
}
