export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080/api/v1";

export const ENDPOINTS = {
  health: `${API_BASE_URL}/health`,
  auth: {
    login: `${API_BASE_URL}/auth/login`,
    token: `${API_BASE_URL}/auth/token`,
    refresh: `${API_BASE_URL}/auth/refresh`,
    logout: `${API_BASE_URL}/auth/logout`,
    me: `${API_BASE_URL}/auth/me`,
  },
  scans: {
    list: `${API_BASE_URL}/scans`,
    create: `${API_BASE_URL}/scans`,
    get: (id: string) => `${API_BASE_URL}/scans/${id}`,
    cancel: (id: string) => `${API_BASE_URL}/scans/${id}/cancel`,
    retry: (id: string) => `${API_BASE_URL}/scans/${id}/retry`,
    progress: (id: string) => `${API_BASE_URL}/scans/${id}/progress`,
    events: (id: string) => `${API_BASE_URL}/scans/${id}/events`,
    report: (id: string) => `${API_BASE_URL}/scans/${id}/report`,
    relationships: (id: string) => `${API_BASE_URL}/scans/${id}/relationships`,
    exportCsv: (id: string) => `${API_BASE_URL}/scans/${id}/export/csv`,
    exportJson: (id: string) => `${API_BASE_URL}/scans/${id}/export/json`,
  },
  accounts: {
    list: (scanId: string) => `${API_BASE_URL}/scans/${scanId}/accounts`,
    detail: (scanId: string, accountId: string) => `${API_BASE_URL}/scans/${scanId}/accounts/${accountId}`,
    evidence: (scanId: string, accountId: string) => `${API_BASE_URL}/scans/${scanId}/accounts/${accountId}/evidence`,
    features: (scanId: string, accountId: string) => `${API_BASE_URL}/scans/${scanId}/accounts/${accountId}/features`,
    neighborhood: (scanId: string, accountId: string) => `${API_BASE_URL}/scans/${scanId}/accounts/${accountId}/neighborhood`,
  },
  capabilities: `${API_BASE_URL}/capabilities`,
  audit: `${API_BASE_URL}/audit`,
  networks: {
    clusters: (scanId: string) => `${API_BASE_URL}/scans/${scanId}/networks/clusters`,
    graph: (scanId: string) => `${API_BASE_URL}/scans/${scanId}/networks/graph`,
    neighbors: (scanId: string, nodeId: string) => `${API_BASE_URL}/scans/${scanId}/networks/nodes/${nodeId}/neighbors`,
    metrics: (scanId: string) => `${API_BASE_URL}/scans/${scanId}/networks/metrics`,
    export: (scanId: string) => `${API_BASE_URL}/scans/${scanId}/networks/export`,
  },
  imports: {
    syntheticDemo: `${API_BASE_URL}/imports/synthetic-demo`,
  },
  adapters: {
    validateUrl: `${API_BASE_URL}/adapters/validate-url`,
    probe: `${API_BASE_URL}/adapters/probe`,
    quotas: `${API_BASE_URL}/adapters/quotas`,
    telemetry: `${API_BASE_URL}/adapters/telemetry`,
  },
} as const;

export const getScanCoordinationEndpoint = (
  scanId: string,
  burstWindowSeconds: number = 60,
  minSimilarityDistance: number = 4
): string => {
  return `${API_BASE_URL}/scans/${encodeURIComponent(scanId)}/coordination?burst_window_seconds=${burstWindowSeconds}&min_similarity_distance=${minSimilarityDistance}`;
};

export const getScanDiffEndpoint = (scanA: string, scanB: string): string => {
  return `${API_BASE_URL}/diff?scan_a=${encodeURIComponent(scanA)}&scan_b=${encodeURIComponent(scanB)}`;
};

export const getSettingsRetentionEndpoint = (days: number = 90): string => {
  return `${API_BASE_URL}/settings/retention?retention_days=${days}`;
};

export const getSettingsQuotasEndpoint = (): string => {
  return `${API_BASE_URL}/settings/quotas`;
};

export const getValidateUrlEndpoint = (): string => `${API_BASE_URL}/adapters/validate-url`;
export const getProbeAccountEndpoint = (): string => `${API_BASE_URL}/adapters/probe`;
export const getAdapterQuotasEndpoint = (): string => `${API_BASE_URL}/adapters/quotas`;
export const getAdapterTelemetryEndpoint = (): string => `${API_BASE_URL}/adapters/telemetry`;

export const endpoints = {
  validateUrl: getValidateUrlEndpoint,
  probeAccount: getProbeAccountEndpoint,
  adapterQuotas: getAdapterQuotasEndpoint,
  adapterTelemetry: getAdapterTelemetryEndpoint,
};
