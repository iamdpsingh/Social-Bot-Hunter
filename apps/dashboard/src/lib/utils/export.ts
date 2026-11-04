export function convertToCsv<T extends Record<string, unknown>>(data: T[]): string {
  if (data.length === 0) return "";
  const headers = Object.keys(data[0]);
  const headerRow = headers.map((h) => `"${h}"`).join(",");
  const rows = data.map((item) =>
    headers
      .map((header) => {
        const val = item[header];
        const str = val === null || val === undefined ? "" : String(val);
        return `"${str.replace(/"/g, '""')}"`;
      })
      .join(",")
  );
  return [headerRow, ...rows].join("\n");
}

export function convertToJsonBundle<T>(metadata: Record<string, unknown>, items: T[]): string {
  return JSON.stringify(
    {
      exported_at: "2026-11-04T12:00:00Z",
      metadata,
      count: items.length,
      data: items,
    },
    null,
    2
  );
}
