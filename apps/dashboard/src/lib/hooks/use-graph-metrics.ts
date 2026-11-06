import { useEffect, useState } from "react";
import { ENDPOINTS } from "../api/endpoints";
import type { GraphMetricsResponse } from "../api/types";

export function useGraphMetrics(scanId: string, token?: string) {
  const [metrics, setMetrics] = useState<GraphMetricsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!scanId) return;

    let mounted = true;
    setLoading(true);

    const headers: Record<string, string> = {};
    if (token) headers.Authorization = `Bearer ${token}`;

    fetch(ENDPOINTS.networks.metrics(scanId), { headers })
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to load network metrics: ${res.status}`);
        return res.json();
      })
      .then((data: GraphMetricsResponse) => {
        if (mounted) {
          setMetrics(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (mounted) {
          setError(err);
          setLoading(false);
        }
      });

    return () => {
      mounted = false;
    };
  }, [scanId, token]);

  return { metrics, loading, error };
}
