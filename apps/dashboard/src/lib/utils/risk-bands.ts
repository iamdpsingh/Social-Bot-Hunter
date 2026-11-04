export type RiskLevel = "MINIMAL" | "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export function scoreToRiskBand(score: number): RiskLevel {
  if (score < 20) return "MINIMAL";
  if (score < 40) return "LOW";
  if (score < 60) return "MEDIUM";
  if (score < 80) return "HIGH";
  return "CRITICAL";
}

export function getRiskBandLabel(level: RiskLevel): string {
  switch (level) {
    case "MINIMAL":
      return "Minimal Risk";
    case "LOW":
      return "Low Risk";
    case "MEDIUM":
      return "Medium Risk";
    case "HIGH":
      return "High Risk";
    case "CRITICAL":
      return "Critical Risk";
  }
}
