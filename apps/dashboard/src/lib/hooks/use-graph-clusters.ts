import { useEffect, useState } from "react";
import { ENDPOINTS } from "../api/endpoints";

export interface ClusterRecord {
  id: string;
  method: string;
  member_count: number;
  confidence: string;
  signal_strength: string;
  members: string[];
}

export function useGraphClusters(scanId: string, token?: string) {
  const [clusters, setClusters] = useState<ClusterRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!scanId) return;

    let mounted = true;
    setLoading(true);

    const headers: Record<string, string> = {};
    if (token) headers.Authorization = `Bearer ${token}`;

    fetch(ENDPOINTS.networks.clusters(scanId), { headers })
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to load clusters: ${res.status}`);
        return res.json();
      })
      .then((data) => {
        if (mounted) {
          setClusters(data.clusters || []);
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

  return { clusters, loading, error };
}
