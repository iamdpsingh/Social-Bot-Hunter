export type SortDirection = "asc" | "desc";

export function compareValues<T>(a: T, b: T, direction: SortDirection = "asc"): number {
  if (a === b) return 0;
  if (a === null || a === undefined) return 1;
  if (b === null || b === undefined) return -1;

  let comparison = 0;
  if (typeof a === "number" && typeof b === "number") {
    comparison = a - b;
  } else if (typeof a === "string" && typeof b === "string") {
    comparison = a.localeCompare(b);
  } else {
    comparison = String(a).localeCompare(String(b));
  }

  return direction === "asc" ? comparison : -comparison;
}

export function sortRecords<T>(
  items: T[],
  key: keyof T,
  direction: SortDirection = "asc"
): T[] {
  return [...items].sort((a, b) => compareValues(a[key], b[key], direction));
}
