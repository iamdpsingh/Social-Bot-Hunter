export const GRAPH_NODE_COLORS: Record<string, { bg: string; border: string; text: string }> = {
  critical: { bg: "#ef4444", border: "#b91c1c", text: "#ffffff" },
  high: { bg: "#f97316", border: "#c2410c", text: "#ffffff" },
  medium: { bg: "#eab308", border: "#a16207", text: "#1e293b" },
  low: { bg: "#22c55e", border: "#15803d", text: "#ffffff" },
  insufficient_evidence: { bg: "#94a3b8", border: "#64748b", text: "#ffffff" },
};

export const GRAPH_NODE_SIZES = {
  sm: 24,
  md: 32,
  lg: 44,
  focal: 50,
} as const;

export const GRAPH_EDGE_COLORS = {
  default: "#94a3b8",
  highlight: "#3b82f6",
  dimmed: "rgba(148, 163, 184, 0.2)",
  cluster: "#a855f7",
} as const;

export const CLUSTER_HULL_PALETTE = [
  "rgba(168, 85, 247, 0.15)", // purple
  "rgba(239, 68, 68, 0.15)",  // red
  "rgba(249, 115, 22, 0.15)", // orange
  "rgba(59, 130, 246, 0.15)", // blue
  "rgba(16, 185, 129, 0.15)", // emerald
  "rgba(236, 72, 153, 0.15)", // pink
];

export const LAYOUT_PRESETS = [
  { id: "cose", label: "Force-Directed (Cose)" },
  { id: "concentric", label: "Concentric by Risk" },
  { id: "circle", label: "Circular" },
  { id: "breadthfirst", label: "Hierarchical" },
  { id: "grid", label: "Compact Grid" },
] as const;

export type LayoutPresetId = (typeof LAYOUT_PRESETS)[number]["id"];
