export function getConcentricLevel(data: { score?: number | null; band?: string | null }): number {
  if (data.score != null) {
    return Math.min(10, Math.max(0, Math.round(data.score * 10)));
  }
  switch (data.band) {
    case "critical":
      return 10;
    case "high":
      return 8;
    case "medium":
      return 5;
    case "low":
      return 2;
    default:
      return 0;
  }
}
