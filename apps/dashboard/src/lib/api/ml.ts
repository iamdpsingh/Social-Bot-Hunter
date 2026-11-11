import { CalibrationCurve, MLModelInfo, MLPredictResult } from '../types/ml';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchModelInfo(token?: string): Promise<MLModelInfo> {
  const headers: HeadersInit = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}/api/v1/detection/ml/model`, { headers });
  if (!res.ok) throw new Error(`Failed to fetch ML model info: ${res.statusText}`);
  return res.json();
}

export async function fetchCalibrationCurve(nBins: number = 10, token?: string): Promise<CalibrationCurve> {
  const headers: HeadersInit = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}/api/v1/detection/ml/calibration?n_bins=${nBins}`, { headers });
  if (!res.ok) throw new Error(`Failed to fetch calibration curve: ${res.statusText}`);
  return res.json();
}

export async function fetchFeatureImportances(token?: string): Promise<Record<string, number>> {
  const headers: HeadersInit = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}/api/v1/detection/ml/feature-importance`, { headers });
  if (!res.ok) throw new Error(`Failed to fetch feature importances: ${res.statusText}`);
  const data = await res.json();
  return data.importances;
}
