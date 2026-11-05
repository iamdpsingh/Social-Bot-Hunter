export function formatSignalWeight(weight: number): string {
  const pct = Math.round(weight * 100);
  return `${pct}%`;
}

export function sortSignalsByImpact<T extends { weight: number }>(signals: T[]): T[] {
  return [...signals].sort((a, b) => b.weight - a.weight);
}
