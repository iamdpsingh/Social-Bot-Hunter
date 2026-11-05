export const RISK_GAUGE_TOKENS = {
  radius: 64,
  strokeWidth: 10,
  circumference: 2 * Math.PI * 64, // ~402.12
  sizes: {
    sm: { width: 96, height: 96, radius: 40, strokeWidth: 8 },
    md: { width: 140, height: 140, radius: 56, strokeWidth: 10 },
    lg: { width: 180, height: 180, radius: 72, strokeWidth: 12 },
  },
  bands: {
    critical: "#EF4444",
    high: "#F97316",
    medium: "#F59E0B",
    low: "#10B981",
    insufficient_evidence: "#6B7280",
  },
} as const;
