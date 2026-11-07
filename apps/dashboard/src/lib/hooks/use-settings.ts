import { useEffect, useState } from "react";
import { getSettingsQuotasEndpoint, getSettingsRetentionEndpoint } from "../api/endpoints";
import type { PlatformQuotaStatus, RetentionStatsResponse } from "../api/types";

export function useRetentionSettings(retentionDays: number = 90) {
  const [stats, setStats] = useState<RetentionStatsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchStats = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const res = await fetch(getSettingsRetentionEndpoint(retentionDays));
      if (!res.ok) throw new Error("Failed to load retention statistics");
      const json = await res.json();
      setStats(json);
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, [retentionDays]);

  return { stats, isLoading, isError: !!error, error, mutate: fetchStats };
}

export function usePlatformQuotas() {
  const [quotas, setQuotas] = useState<PlatformQuotaStatus[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchQuotas = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const res = await fetch(getSettingsQuotasEndpoint());
      if (!res.ok) throw new Error("Failed to load platform quotas");
      const json = await res.json();
      setQuotas(json);
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchQuotas();
  }, []);

  return { quotas, isLoading, isError: !!error, error, mutate: fetchQuotas };
}
