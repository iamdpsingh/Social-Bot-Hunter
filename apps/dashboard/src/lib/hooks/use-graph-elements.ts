import { useEffect, useState } from "react";
import { ENDPOINTS } from "../api/endpoints";
import type { CytoscapeGraphResponse } from "../api/types";

export interface UseGraphElementsOptions {
  maxNodes?: number;
  clusterId?: string;
  riskBand?: string;
  minScore?: number;
  token?: string;
}

export function useGraphElements(scanId: string, options: UseGraphElementsOptions = {}) {
  const [data, setData] = useState<CytoscapeGraphResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const { maxNodes = 500, clusterId, riskBand, minScore, token } = options;

  useEffect(() => {
    if (!scanId) return;

    let mounted = true;
    setLoading(true);
    setError(null);

    const url = new URL(ENDPOINTS.networks.graph(scanId));
    url.searchParams.set("max_nodes", String(maxNodes));
    if (clusterId) url.searchParams.set("cluster_id", clusterId);
    if (riskBand) url.searchParams.set("risk_band", riskBand);
    if (minScore !== undefined) url.searchParams.set("min_score", String(minScore));

    const headers: Record<string, string> = {};
    if (token) headers.Authorization = `Bearer ${token}`;

    fetch(url.toString(), { credentials: "omit", headers })
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to load graph elements: ${res.status}`);
        return res.json();
      })
      .then((json: CytoscapeGraphResponse) => {
        if (mounted) {
          setData(json);
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
  }, [scanId, maxNodes, clusterId, riskBand, minScore, token]);

  return { data, loading, error };
}
