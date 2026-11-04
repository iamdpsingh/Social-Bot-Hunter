export type RiskBand = "critical" | "high" | "medium" | "low" | "insufficient_evidence";

export interface RiskBandDefinition {
  band: RiskBand;
  label: string;
  minScore: number;
  maxScore: number;
  color: string;
  bgColor: string;
  borderColor: string;
  badgeVariant: "destructive" | "warning" | "default" | "success" | "secondary";
  iconName: string;
  description: string;
}

export const RISK_BANDS: Record<RiskBand, RiskBandDefinition> = {
  critical: {
    band: "critical",
    label: "Critical Risk",
    minScore: 0.8,
    maxScore: 1.0,
    color: "#EF4444",
    bgColor: "rgba(239, 68, 68, 0.12)",
    borderColor: "rgba(239, 68, 68, 0.35)",
    badgeVariant: "destructive",
    iconName: "ShieldAlert",
    description: "Extremely high probability of automated or coordinated activity. Multiple heuristic and graph signals triggered.",
  },
  high: {
    band: "high",
    label: "High Risk",
    minScore: 0.6,
    maxScore: 0.799,
    color: "#F97316",
    bgColor: "rgba(249, 115, 22, 0.12)",
    borderColor: "rgba(249, 115, 22, 0.35)",
    badgeVariant: "warning",
    iconName: "AlertTriangle",
    description: "Strong indicators of automation or synthetic behavior. Investigation recommended.",
  },
  medium: {
    band: "medium",
    label: "Medium Risk",
    minScore: 0.35,
    maxScore: 0.599,
    color: "#F59E0B",
    bgColor: "rgba(245, 158, 11, 0.12)",
    borderColor: "rgba(245, 158, 11, 0.35)",
    badgeVariant: "default",
    iconName: "AlertCircle",
    description: "Anomalous signals observed, but insufficient for definitive classification. Potential false positive.",
  },
  low: {
    band: "low",
    label: "Low Risk",
    minScore: 0.0,
    maxScore: 0.349,
    color: "#10B981",
    bgColor: "rgba(16, 185, 129, 0.12)",
    borderColor: "rgba(16, 185, 129, 0.35)",
    badgeVariant: "success",
    iconName: "ShieldCheck",
    description: "Behavior consistent with organic human activity within available coverage limits.",
  },
  insufficient_evidence: {
    band: "insufficient_evidence",
    label: "Insufficient Evidence",
    minScore: -1,
    maxScore: -1,
    color: "#6B7280",
    bgColor: "rgba(107, 114, 128, 0.12)",
    borderColor: "rgba(107, 114, 128, 0.35)",
    badgeVariant: "secondary",
    iconName: "HelpCircle",
    description: "Key features unobservable due to platform API restrictions or incomplete data collection.",
  },
};

export function getRiskBand(score: number | null | undefined): RiskBandDefinition {
  if (score === null || score === undefined || score < 0) {
    return RISK_BANDS.insufficient_evidence;
  }
  if (score >= 0.8) return RISK_BANDS.critical;
  if (score >= 0.6) return RISK_BANDS.high;
  if (score >= 0.35) return RISK_BANDS.medium;
  return RISK_BANDS.low;
}
