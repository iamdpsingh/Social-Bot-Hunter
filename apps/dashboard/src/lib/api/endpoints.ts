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
  imports: {
    syntheticDemo: `${API_BASE_URL}/imports/synthetic-demo`,
  },
} as const;
