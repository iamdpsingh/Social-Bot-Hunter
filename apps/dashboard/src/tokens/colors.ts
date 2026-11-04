export const PALETTE = {
  midnight: {
    950: "#020617",
    900: "#0F172A",
    800: "#1E293B",
    700: "#334155",
  },
  cyber: {
    500: "#3B82F6",
    600: "#2563EB",
    400: "#60A5FA",
  },
  risk: {
    critical: "#EF4444",
    high: "#F97316",
    medium: "#F59E0B",
    low: "#10B981",
    unknown: "#6B7280",
  },
  status: {
    pending: "#94A3B8",
    running: "#3B82F6",
    complete: "#10B981",
    partial: "#EAB308",
    failed: "#EF4444",
    cancelled: "#64748B",
  },
} as const;

export type ColorPalette = typeof PALETTE;
