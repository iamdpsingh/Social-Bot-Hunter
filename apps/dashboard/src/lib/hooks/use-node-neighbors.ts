import { useEffect, useState } from "react";
import { ENDPOINTS } from "../api/endpoints";
import type { NodeNeighborsResponse } from "../api/types";

export function useNodeNeighbors(
  scanId: string,
  nodeId: string | null,
  direction = "both",
  radius = 1,
  token?: string
) {
  const [data, setData] = useState<NodeNeighborsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!scanId || !nodeId) {
      setData(null);
      setLoading(false);
      return;
    }

    let mounted = true;
    setLoading(true);
    setError(null);

    const url = new URL(ENDPOINTS.networks.neighbors(scanId, nodeId));
    url.searchParams.set("direction", direction);
    url.searchParams.set("radius", String(radius));

    const headers: Record<string, string> = {};
    if (token) headers.Authorization = `Bearer ${token}`;

    fetch(url.toString(), { headers })
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to load neighbors: ${res.status}`);
        return res.json();
      })
      .then((json: NodeNeighborsResponse) => {
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
  }, [scanId, nodeId, direction, radius, token]);

  return { data, loading, error };
}
