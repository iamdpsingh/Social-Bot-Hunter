import { useEffect, useState } from "react";
import { getScanDiffEndpoint } from "../api/endpoints";
import type { ScanDiffResponse } from "../api/types";

export function useScanDiff(scanAId: string, scanBId: string) {
  const [diff, setDiff] = useState<ScanDiffResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!scanAId || !scanBId) {
      setDiff(null);
      setIsLoading(false);
      return;
    }

    let mounted = true;
    setIsLoading(true);
    setError(null);

    const url = getScanDiffEndpoint(scanAId, scanBId);
    fetch(url)
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Failed to compare scans: ${res.statusText}`);
        }
        return res.json();
      })
      .then((data) => {
        if (mounted) setDiff(data);
      })
      .catch((err) => {
        if (mounted) setError(err instanceof Error ? err : new Error(String(err)));
      })
      .finally(() => {
        if (mounted) setIsLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, [scanAId, scanBId]);

  return { diff, isLoading, isError: !!error, error };
}
