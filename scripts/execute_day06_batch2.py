from __future__ import annotations

import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DAY_START = datetime(2026, 11, 6, 10, 40, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
AUTHOR_NAME = "dpsingh"
AUTHOR_EMAIL = "dhruvpratapsingh30.official2.o@gmail.com"

commit_idx = 0

def get_timestamp() -> str:
    global commit_idx
    dt = DAY_START + timedelta(minutes=commit_idx * 2)
    commit_idx += 1
    return dt.isoformat()

def commit_file(rel_path: str, msg: str) -> None:
    time_str = get_timestamp()
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = AUTHOR_NAME
    env["GIT_AUTHOR_EMAIL"] = AUTHOR_EMAIL
    env["GIT_AUTHOR_DATE"] = time_str
    env["GIT_COMMITTER_NAME"] = AUTHOR_NAME
    env["GIT_COMMITTER_EMAIL"] = AUTHOR_EMAIL
    env["GIT_COMMITTER_DATE"] = time_str

    full_path = REPO_ROOT / rel_path
    if not full_path.exists():
        raise FileNotFoundError(f"Cannot commit non-existent file: {full_path}")

    if rel_path.endswith(".py"):
        subprocess.run(
            [str(REPO_ROOT / ".venv/bin/python"), "-m", "ruff", "check", "--fix", rel_path],
            cwd=REPO_ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    subprocess.run(["git", "add", rel_path], check=True, cwd=REPO_ROOT)
    res = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO_ROOT)
    if res.returncode != 0:
        subprocess.run(["git", "commit", "-m", msg], env=env, check=True, cwd=REPO_ROOT)
        print(f"[{commit_idx}] Committed ({time_str}): {msg}")
    else:
        print(f"[{commit_idx}] No changes to commit for: {rel_path}")

def write_and_commit(rel_path: str, content: str, msg: str) -> None:
    full_path = REPO_ROOT / rel_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content.strip() + "\n", encoding="utf-8")
    commit_file(rel_path, msg)

print("Starting Day 6 Batch 2: Frontend Graph Tokens, Stylesheet, Layouts, Transforms & Hooks...")

# 1. apps/dashboard/src/tokens/graph.ts
write_and_commit(
    "apps/dashboard/src/tokens/graph.ts",
    """export const GRAPH_NODE_COLORS: Record<string, { bg: string; border: string; text: string }> = {
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
""",
    "feat(tokens): create graph design tokens for nodes, edges, hulls, and layout presets"
)

# 2. apps/dashboard/src/tokens/__tests__/graph-tokens.test.ts
write_and_commit(
    "apps/dashboard/src/tokens/__tests__/graph-tokens.test.ts",
    """import { describe, expect, it } from "vitest";
import {
  CLUSTER_HULL_PALETTE,
  GRAPH_EDGE_COLORS,
  GRAPH_NODE_COLORS,
  GRAPH_NODE_SIZES,
  LAYOUT_PRESETS,
} from "../graph";

describe("graph tokens", () => {
  it("defines node colors for all five risk bands", () => {
    expect(GRAPH_NODE_COLORS.critical.bg).toBe("#ef4444");
    expect(GRAPH_NODE_COLORS.high.bg).toBe("#f97316");
    expect(GRAPH_NODE_COLORS.medium.bg).toBe("#eab308");
    expect(GRAPH_NODE_COLORS.low.bg).toBe("#22c55e");
    expect(GRAPH_NODE_COLORS.insufficient_evidence.bg).toBe("#94a3b8");
  });

  it("defines standard node sizes including focal node", () => {
    expect(GRAPH_NODE_SIZES.sm).toBe(24);
    expect(GRAPH_NODE_SIZES.focal).toBe(50);
  });

  it("exports 5 layout presets", () => {
    expect(LAYOUT_PRESETS).toHaveLength(5);
    expect(LAYOUT_PRESETS.map((p) => p.id)).toContain("cose");
    expect(LAYOUT_PRESETS.map((p) => p.id)).toContain("concentric");
  });

  it("defines at least 5 cluster hull colors", () => {
    expect(CLUSTER_HULL_PALETTE.length).toBeGreaterThanOrEqual(5);
  });
});
""",
    "test(tokens): test graph design tokens risk palettes, sizes, and layout presets"
)

# 3. Update apps/dashboard/src/lib/api/types.ts
types_path = REPO_ROOT / "apps/dashboard/src/lib/api/types.ts"
types_text = types_path.read_text(encoding="utf-8")
additional_types = """
export interface CytoscapeNodeData {
  id: string;
  label?: string;
  score?: number | null;
  band?: string | null;
  cluster_id?: string | null;
  [key: string]: any;
}

export interface CytoscapeEdgeData {
  id: string;
  source: string;
  target: string;
  type?: string;
  relationship_type?: string;
  [key: string]: any;
}

export interface CytoscapeElement {
  data: CytoscapeNodeData | CytoscapeEdgeData;
}

export interface CytoscapeGraphElements {
  nodes: Array<{ data: CytoscapeNodeData }>;
  edges: Array<{ data: CytoscapeEdgeData }>;
}

export interface CytoscapeGraphResponse {
  scan_id: string;
  elements: CytoscapeGraphElements;
  node_count: number;
  edge_count: number;
}

export interface NodeNeighborItem {
  node_id: string;
  direction: "inbound" | "outbound" | string;
  relationship_type: string;
  risk_score?: number | null;
  risk_band?: string | null;
}

export interface NodeNeighborsResponse {
  scan_id: string;
  center_node_id: string;
  direction: string;
  radius: number;
  neighbors: NodeNeighborItem[];
  total: number;
}

export interface GraphMetricsResponse {
  scan_id: string;
  node_count: number;
  edge_count: number;
  density: number;
  reciprocity: number;
  weakly_connected_components: number;
  strongly_connected_components: number;
  avg_in_degree: number;
  avg_out_degree: number;
}

export interface GraphExportBundleResponse {
  scan_id: string;
  format: string;
  elements: CytoscapeGraphElements;
  metrics: Record<string, any>;
  exported_at: string;
}
"""
if "CytoscapeGraphResponse" not in types_text:
    types_text = types_text.rstrip() + "\n" + additional_types.strip() + "\n"
    types_path.write_text(types_text, encoding="utf-8")
commit_file("apps/dashboard/src/lib/api/types.ts", "feat(types): add Cytoscape graph, neighbor expansion, and network metrics types")

# 4. apps/dashboard/src/lib/api/__tests__/graph-types.test.ts
write_and_commit(
    "apps/dashboard/src/lib/api/__tests__/graph-types.test.ts",
    """import { describe, expect, it } from "vitest";
import type {
  CytoscapeGraphResponse,
  GraphExportBundleResponse,
  GraphMetricsResponse,
  NodeNeighborsResponse,
} from "../types";

describe("graph api types contract", () => {
  it("validates CytoscapeGraphResponse structural type assignment", () => {
    const res: CytoscapeGraphResponse = {
      scan_id: "s_123",
      elements: {
        nodes: [{ data: { id: "node_1", score: 0.95, band: "critical" } }],
        edges: [{ data: { id: "node_1->node_2", source: "node_1", target: "node_2" } }],
      },
      node_count: 1,
      edge_count: 1,
    };
    expect(res.scan_id).toBe("s_123");
    expect(res.elements.nodes).toHaveLength(1);
  });

  it("validates NodeNeighborsResponse and GraphMetricsResponse structures", () => {
    const neighbors: NodeNeighborsResponse = {
      scan_id: "s_1",
      center_node_id: "focal",
      direction: "both",
      radius: 1,
      neighbors: [
        {
          node_id: "peer_1",
          direction: "inbound",
          relationship_type: "follower",
          risk_score: 0.82,
          risk_band: "high",
        },
      ],
      total: 1,
    };
    expect(neighbors.neighbors[0].risk_band).toBe("high");

    const metrics: GraphMetricsResponse = {
      scan_id: "s_1",
      node_count: 50,
      edge_count: 120,
      density: 0.048,
      reciprocity: 0.22,
      weakly_connected_components: 2,
      strongly_connected_components: 12,
      avg_in_degree: 2.4,
      avg_out_degree: 2.4,
    };
    expect(metrics.density).toBe(0.048);
  });
});
""",
    "test(types): test CytoscapeGraphResponse, neighbors, and metrics type contracts"
)

# 5. Update apps/dashboard/src/lib/api/endpoints.ts
endpoints_path = REPO_ROOT / "apps/dashboard/src/lib/api/endpoints.ts"
endpoints_text = endpoints_path.read_text(encoding="utf-8")
networks_endpoint_block = """  networks: {
    clusters: (scanId: string) => `${API_BASE_URL}/scans/${scanId}/networks/clusters`,
    graph: (scanId: string) => `${API_BASE_URL}/scans/${scanId}/networks/graph`,
    neighbors: (scanId: string, nodeId: string) => `${API_BASE_URL}/scans/${scanId}/networks/nodes/${nodeId}/neighbors`,
    metrics: (scanId: string) => `${API_BASE_URL}/scans/${scanId}/networks/metrics`,
    export: (scanId: string) => `${API_BASE_URL}/scans/${scanId}/networks/export`,
  },
"""
if "networks:" not in endpoints_text:
    endpoints_text = endpoints_text.replace(
        "  imports: {",
        networks_endpoint_block + "  imports: {"
    )
    endpoints_path.write_text(endpoints_text, encoding="utf-8")
commit_file("apps/dashboard/src/lib/api/endpoints.ts", "feat(api): add networks graph, clusters, neighbors, metrics, and export endpoints")

# 6. apps/dashboard/src/lib/api/__tests__/graph-endpoints.test.ts
write_and_commit(
    "apps/dashboard/src/lib/api/__tests__/graph-endpoints.test.ts",
    """import { describe, expect, it } from "vitest";
import { ENDPOINTS } from "../endpoints";

describe("networks graph endpoints", () => {
  it("generates correct paths for network subrouter", () => {
    expect(ENDPOINTS.networks.clusters("scan_99")).toContain("/scans/scan_99/networks/clusters");
    expect(ENDPOINTS.networks.graph("scan_99")).toContain("/scans/scan_99/networks/graph");
    expect(ENDPOINTS.networks.neighbors("scan_99", "node_1")).toContain("/scans/scan_99/networks/nodes/node_1/neighbors");
    expect(ENDPOINTS.networks.metrics("scan_99")).toContain("/scans/scan_99/networks/metrics");
    expect(ENDPOINTS.networks.export("scan_99")).toContain("/scans/scan_99/networks/export");
  });
});
""",
    "test(api): test network graph endpoint URL generator routes"
)

# 7. apps/dashboard/src/lib/graph/stylesheet.ts
write_and_commit(
    "apps/dashboard/src/lib/graph/stylesheet.ts",
    """import type { StylesheetStyle } from "cytoscape";
import { GRAPH_EDGE_COLORS, GRAPH_NODE_COLORS, GRAPH_NODE_SIZES } from "../../tokens/graph";

export function getCytoscapeStylesheet(): StylesheetStyle[] {
  return [
    {
      selector: "node",
      style: {
        width: GRAPH_NODE_SIZES.md,
        height: GRAPH_NODE_SIZES.md,
        "background-color": GRAPH_NODE_COLORS.insufficient_evidence.bg,
        label: "data(label)",
        "font-size": "10px",
        "font-family": "Inter, ui-sans-serif, system-ui",
        "text-valign": "bottom",
        "text-margin-y": 4,
        color: "#475569",
        "border-width": 1.5,
        "border-color": "#ffffff",
        "transition-property": "background-color, border-color, opacity, width, height",
        "transition-duration": 0.2,
      },
    },
    {
      selector: "node[band = 'critical']",
      style: {
        "background-color": GRAPH_NODE_COLORS.critical.bg,
        "border-color": GRAPH_NODE_COLORS.critical.border,
      },
    },
    {
      selector: "node[band = 'high']",
      style: {
        "background-color": GRAPH_NODE_COLORS.high.bg,
        "border-color": GRAPH_NODE_COLORS.high.border,
      },
    },
    {
      selector: "node[band = 'medium']",
      style: {
        "background-color": GRAPH_NODE_COLORS.medium.bg,
        "border-color": GRAPH_NODE_COLORS.medium.border,
      },
    },
    {
      selector: "node[band = 'low']",
      style: {
        "background-color": GRAPH_NODE_COLORS.low.bg,
        "border-color": GRAPH_NODE_COLORS.low.border,
      },
    },
    {
      selector: "node:selected",
      style: {
        width: GRAPH_NODE_SIZES.focal,
        height: GRAPH_NODE_SIZES.focal,
        "border-width": 3,
        "border-color": "#2563eb",
        "font-weight": "bold",
        color: "#0f172a",
      },
    },
    {
      selector: "node.highlighted",
      style: {
        "border-width": 2.5,
        "border-color": "#3b82f6",
        opacity: 1,
      },
    },
    {
      selector: "node.dimmed",
      style: {
        opacity: 0.25,
      },
    },
    {
      selector: "edge",
      style: {
        width: 1.5,
        "line-color": GRAPH_EDGE_COLORS.default,
        "target-arrow-color": GRAPH_EDGE_COLORS.default,
        "target-arrow-shape": "triangle",
        "curve-style": "bezier",
        "arrow-scale": 0.9,
        opacity: 0.75,
        "transition-property": "line-color, target-arrow-color, width, opacity",
        "transition-duration": 0.2,
      },
    },
    {
      selector: "edge.highlighted",
      style: {
        width: 2.5,
        "line-color": GRAPH_EDGE_COLORS.highlight,
        "target-arrow-color": GRAPH_EDGE_COLORS.highlight,
        opacity: 1,
        "z-index": 10,
      },
    },
    {
      selector: "edge.dimmed",
      style: {
        opacity: 0.1,
      },
    },
  ];
}
""",
    "feat(graph): implement getCytoscapeStylesheet for directed network visualization"
)

# 8. apps/dashboard/src/lib/graph/__tests__/stylesheet.test.ts
write_and_commit(
    "apps/dashboard/src/lib/graph/__tests__/stylesheet.test.ts",
    """import { describe, expect, it } from "vitest";
import { getCytoscapeStylesheet } from "../stylesheet";

describe("cytoscape stylesheet", () => {
  it("returns stylesheet array containing node, edge, and state selectors", () => {
    const sheet = getCytoscapeStylesheet();
    expect(Array.isArray(sheet)).toBe(true);

    const selectors = sheet.map((s) => s.selector);
    expect(selectors).toContain("node");
    expect(selectors).toContain("edge");
    expect(selectors).toContain("node[band = 'critical']");
    expect(selectors).toContain("node:selected");
    expect(selectors).toContain("node.highlighted");
    expect(selectors).toContain("node.dimmed");
    expect(selectors).toContain("edge.highlighted");
  });

  it("configures bezier curves with arrows for directed edges", () => {
    const sheet = getCytoscapeStylesheet();
    const edgeRule = sheet.find((s) => s.selector === "edge");
    expect(edgeRule?.style?.["curve-style"]).toBe("bezier");
    expect(edgeRule?.style?.["target-arrow-shape"]).toBe("triangle");
  });
});
""",
    "test(graph): test getCytoscapeStylesheet selectors and directed arrow styles"
)

# 9. apps/dashboard/src/lib/graph/layouts.ts
write_and_commit(
    "apps/dashboard/src/lib/graph/layouts.ts",
    """import type { LayoutOptions } from "cytoscape";
import type { LayoutPresetId } from "../../tokens/graph";

export function getLayoutOptions(
  preset: LayoutPresetId,
  options?: Partial<LayoutOptions>
): LayoutOptions {
  switch (preset) {
    case "cose":
      return {
        name: "cose",
        animate: true,
        animationDuration: 500,
        componentSpacing: 60,
        nodeOverlap: 20,
        idealEdgeLength: () => 100,
        edgeElasticity: () => 100,
        nestingFactor: 5,
        gravity: 80,
        numIter: 1000,
        initialTemp: 200,
        coolingFactor: 0.95,
        minTemp: 1.0,
        ...options,
      } as LayoutOptions;

    case "concentric":
      return {
        name: "concentric",
        animate: true,
        animationDuration: 400,
        concentric: (node: any) => {
          const score = node.data("score");
          if (score != null) return Math.round(score * 10);
          const band = node.data("band");
          if (band === "critical") return 10;
          if (band === "high") return 8;
          if (band === "medium") return 5;
          if (band === "low") return 2;
          return 0;
        },
        levelWidth: () => 2,
        minNodeSpacing: 35,
        ...options,
      } as LayoutOptions;

    case "circle":
      return {
        name: "circle",
        animate: true,
        animationDuration: 400,
        spacingFactor: 1.2,
        ...options,
      } as LayoutOptions;

    case "breadthfirst":
      return {
        name: "breadthfirst",
        animate: true,
        animationDuration: 400,
        directed: true,
        spacingFactor: 1.3,
        ...options,
      } as LayoutOptions;

    case "grid":
      return {
        name: "grid",
        animate: true,
        animationDuration: 300,
        spacingFactor: 1.1,
        ...options,
      } as LayoutOptions;

    default:
      return {
        name: "cose",
        animate: false,
        ...options,
      } as LayoutOptions;
  }
}
""",
    "feat(graph): implement getLayoutOptions supporting cose, concentric, circle, breadthfirst, and grid"
)

# 10. apps/dashboard/src/lib/graph/__tests__/layouts.test.ts
write_and_commit(
    "apps/dashboard/src/lib/graph/__tests__/layouts.test.ts",
    """import { describe, expect, it } from "vitest";
import { getLayoutOptions } from "../layouts";

describe("cytoscape layouts", () => {
  it("returns cose force-directed configuration", () => {
    const layout = getLayoutOptions("cose");
    expect(layout.name).toBe("cose");
    expect(layout.animate).toBe(true);
  });

  it("returns concentric layout with risk score weighting", () => {
    const layout = getLayoutOptions("concentric") as any;
    expect(layout.name).toBe("concentric");
    expect(typeof layout.concentric).toBe("function");

    // mock node with score 0.8
    const mockNodeHigh = { data: (k: string) => (k === "score" ? 0.8 : undefined) };
    expect(layout.concentric(mockNodeHigh)).toBe(8);

    // mock node with critical band
    const mockNodeCrit = { data: (k: string) => (k === "band" ? "critical" : undefined) };
    expect(layout.concentric(mockNodeCrit)).toBe(10);
  });

  it("returns circle, breadthfirst, and grid layout presets", () => {
    expect(getLayoutOptions("circle").name).toBe("circle");
    expect(getLayoutOptions("breadthfirst").name).toBe("breadthfirst");
    expect(getLayoutOptions("grid").name).toBe("grid");
  });
});
""",
    "test(graph): test layout presets generation and concentric risk weighting"
)

# 11. apps/dashboard/src/lib/graph/transform.ts
write_and_commit(
    "apps/dashboard/src/lib/graph/transform.ts",
    """import type { CytoscapeGraphElements } from "../api/types";

export interface GraphFilterOptions {
  minScore?: number;
  riskBand?: string;
  clusterId?: string;
  query?: string;
}

export function filterCytoscapeElements(
  elements: CytoscapeGraphElements,
  filters: GraphFilterOptions
): CytoscapeGraphElements {
  const { minScore, riskBand, clusterId, query } = filters;
  const q = query?.trim().toLowerCase();

  const matchingNodes = elements.nodes.filter((n) => {
    const data = n.data;
    if (minScore !== undefined && data.score != null && data.score < minScore) {
      return false;
    }
    if (riskBand && data.band !== riskBand) {
      return false;
    }
    if (clusterId && data.cluster_id !== clusterId) {
      return false;
    }
    if (q) {
      const idMatch = data.id.toLowerCase().includes(q);
      const labelMatch = data.label ? data.label.toLowerCase().includes(q) : false;
      if (!idMatch && !labelMatch) return false;
    }
    return true;
  });

  const matchingNodeIds = new Set(matchingNodes.map((n) => n.data.id));

  const matchingEdges = elements.edges.filter((e) => {
    return matchingNodeIds.has(e.data.source) && matchingNodeIds.has(e.data.target);
  });

  return {
    nodes: matchingNodes,
    edges: matchingEdges,
  };
}

export function getGraphSummaryStats(elements: CytoscapeGraphElements) {
  const nodeCount = elements.nodes.length;
  const edgeCount = elements.edges.length;

  const bandCounts: Record<string, number> = {};
  elements.nodes.forEach((n) => {
    const band = n.data.band || "insufficient_evidence";
    bandCounts[band] = (bandCounts[band] || 0) + 1;
  });

  return {
    nodeCount,
    edgeCount,
    bandCounts,
  };
}
""",
    "feat(graph): implement filterCytoscapeElements and getGraphSummaryStats"
)

# 12. apps/dashboard/src/lib/graph/__tests__/transform.test.ts
write_and_commit(
    "apps/dashboard/src/lib/graph/__tests__/transform.test.ts",
    """import { describe, expect, it } from "vitest";
import type { CytoscapeGraphElements } from "../../api/types";
import { filterCytoscapeElements, getGraphSummaryStats } from "../transform";

describe("graph transform and filtering", () => {
  const sampleElements: CytoscapeGraphElements = {
    nodes: [
      { data: { id: "bot_1", label: "Alpha Bot", score: 0.95, band: "critical", cluster_id: "c_1" } },
      { data: { id: "bot_2", label: "Beta Bot", score: 0.72, band: "high", cluster_id: "c_1" } },
      { data: { id: "innocent", label: "Real User", score: 0.1, band: "low" } },
    ],
    edges: [
      { data: { id: "bot_1->bot_2", source: "bot_1", target: "bot_2" } },
      { data: { id: "bot_2->innocent", source: "bot_2", target: "innocent" } },
    ],
  };

  it("filters nodes by minimum score threshold and strips orphan edges", () => {
    const filtered = filterCytoscapeElements(sampleElements, { minScore: 0.7 });
    expect(filtered.nodes).toHaveLength(2);
    expect(filtered.edges).toHaveLength(1);
    expect(filtered.edges[0].data.id).toBe("bot_1->bot_2");
  });

  it("filters by cluster id", () => {
    const filtered = filterCytoscapeElements(sampleElements, { clusterId: "c_1" });
    expect(filtered.nodes).toHaveLength(2);
  });

  it("filters by text query on label or id", () => {
    const filtered = filterCytoscapeElements(sampleElements, { query: "alpha" });
    expect(filtered.nodes).toHaveLength(1);
    expect(filtered.nodes[0].data.id).toBe("bot_1");
  });

  it("computes summary stats including risk band distributions", () => {
    const stats = getGraphSummaryStats(sampleElements);
    expect(stats.nodeCount).toBe(3);
    expect(stats.edgeCount).toBe(2);
    expect(stats.bandCounts.critical).toBe(1);
    expect(stats.bandCounts.low).toBe(1);
  });
});
""",
    "test(graph): test filterCytoscapeElements and getGraphSummaryStats calculations"
)

# 13. apps/dashboard/src/lib/graph/export.ts
write_and_commit(
    "apps/dashboard/src/lib/graph/export.ts",
    """import type { Core } from "cytoscape";

export function exportGraphPng(cy: Core, filename = "network-graph.png"): void {
  try {
    const pngUri = cy.png({
      output: "blob",
      bg: "#ffffff",
      full: true,
      scale: 2,
    }) as any;

    const url = URL.createObjectURL(pngUri);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  } catch (err) {
    console.error("Failed to export graph PNG:", err);
  }
}

export function exportGraphJson(cy: Core, filename = "network-graph.json"): void {
  try {
    const jsonStr = JSON.stringify(cy.json(), null, 2);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  } catch (err) {
    console.error("Failed to export graph JSON:", err);
  }
}
""",
    "feat(graph): implement exportGraphPng and exportGraphJson helpers"
)

# 14. apps/dashboard/src/lib/graph/__tests__/export.test.ts
write_and_commit(
    "apps/dashboard/src/lib/graph/__tests__/export.test.ts",
    """import { describe, expect, it, vi } from "vitest";
import { exportGraphJson, exportGraphPng } from "../export";

describe("graph export utilities", () => {
  it("triggers JSON file download from cytoscape instance", () => {
    const mockCy: any = {
      json: () => ({ elements: { nodes: [], edges: [] } }),
    };

    const createObjectURL = vi.fn().mockReturnValue("blob:mock-url");
    const revokeObjectURL = vi.fn();
    (global as any).URL.createObjectURL = createObjectURL;
    (global as any).URL.revokeObjectURL = revokeObjectURL;

    exportGraphJson(mockCy, "test.json");
    expect(createObjectURL).toHaveBeenCalled();
    expect(revokeObjectURL).toHaveBeenCalled();
  });

  it("triggers PNG snapshot export from cytoscape instance", () => {
    const mockBlob = new Blob([]);
    const mockCy: any = {
      png: vi.fn().mockReturnValue(mockBlob),
    };

    const createObjectURL = vi.fn().mockReturnValue("blob:mock-png");
    const revokeObjectURL = vi.fn();
    (global as any).URL.createObjectURL = createObjectURL;
    (global as any).URL.revokeObjectURL = revokeObjectURL;

    exportGraphPng(mockCy, "test.png");
    expect(mockCy.png).toHaveBeenCalledWith(
      expect.objectContaining({ full: true, scale: 2, bg: "#ffffff" })
    );
  });
});
""",
    "test(graph): test exportGraphJson and exportGraphPng file download triggers"
)

# 15. apps/dashboard/src/lib/graph/concentric.ts
write_and_commit(
    "apps/dashboard/src/lib/graph/concentric.ts",
    """export function getConcentricLevel(data: { score?: number | null; band?: string | null }): number {
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
""",
    "feat(graph): implement getConcentricLevel utility for concentric layout hierarchy"
)

# 16. apps/dashboard/src/lib/graph/__tests__/concentric.test.ts
write_and_commit(
    "apps/dashboard/src/lib/graph/__tests__/concentric.test.ts",
    """import { describe, expect, it } from "vitest";
import { getConcentricLevel } from "../concentric";

describe("getConcentricLevel", () => {
  it("calculates level based on risk score (0-10)", () => {
    expect(getConcentricLevel({ score: 0.95 })).toBe(10);
    expect(getConcentricLevel({ score: 0.52 })).toBe(5);
    expect(getConcentricLevel({ score: 0.12 })).toBe(1);
    expect(getConcentricLevel({ score: 0.0 })).toBe(0);
  });

  it("falls back to risk band when score is absent", () => {
    expect(getConcentricLevel({ band: "critical" })).toBe(10);
    expect(getConcentricLevel({ band: "high" })).toBe(8);
    expect(getConcentricLevel({ band: "medium" })).toBe(5);
    expect(getConcentricLevel({ band: "low" })).toBe(2);
    expect(getConcentricLevel({ band: "unknown" })).toBe(0);
  });
});
""",
    "test(graph): test getConcentricLevel score and band fallbacks"
)

# 17. apps/dashboard/src/lib/graph/cluster-hull.ts
write_and_commit(
    "apps/dashboard/src/lib/graph/cluster-hull.ts",
    """export interface Point {
  x: number;
  y: number;
}

export function crossProduct(o: Point, a: Point, b: Point): number {
  return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x);
}

export function computeConvexHull(points: Point[]): Point[] {
  if (points.length <= 1) return [...points];
  if (points.length === 2) return [...points];

  const sorted = [...points].sort((a, b) => (a.x === b.x ? a.y - b.y : a.x - b.x));

  const lower: Point[] = [];
  for (const p of sorted) {
    while (lower.length >= 2 && crossProduct(lower[lower.length - 2], lower[lower.length - 1], p) <= 0) {
      lower.pop();
    }
    lower.push(p);
  }

  const upper: Point[] = [];
  for (let i = sorted.length - 1; i >= 0; i--) {
    const p = sorted[i];
    while (upper.length >= 2 && crossProduct(upper[upper.length - 2], upper[upper.length - 1], p) <= 0) {
      upper.pop();
    }
    upper.push(p);
  }

  lower.pop();
  upper.pop();
  return lower.concat(upper);
}
""",
    "feat(graph): implement computeConvexHull for botnet cluster hull visualization"
)

# 18. apps/dashboard/src/lib/graph/__tests__/cluster-hull.test.ts
write_and_commit(
    "apps/dashboard/src/lib/graph/__tests__/cluster-hull.test.ts",
    """import { describe, expect, it } from "vitest";
import { computeConvexHull, crossProduct } from "../cluster-hull";

describe("cluster hull algorithms", () => {
  it("calculates 2D cross product", () => {
    const o = { x: 0, y: 0 };
    const a = { x: 1, y: 0 };
    const b = { x: 0, y: 1 };
    expect(crossProduct(o, a, b)).toBe(1);
  });

  it("computes convex hull of a point set", () => {
    const points = [
      { x: 0, y: 0 },
      { x: 10, y: 0 },
      { x: 10, y: 10 },
      { x: 0, y: 10 },
      { x: 5, y: 5 }, // interior point
    ];
    const hull = computeConvexHull(points);
    expect(hull).toHaveLength(4);
    expect(hull.some((p) => p.x === 5 && p.y === 5)).toBe(false);
  });

  it("handles small point sets safely", () => {
    expect(computeConvexHull([])).toEqual([]);
    expect(computeConvexHull([{ x: 1, y: 2 }])).toEqual([{ x: 1, y: 2 }]);
  });
});
""",
    "test(graph): test computeConvexHull Monotone Chain polygon vertices calculation"
)

# 19. apps/dashboard/src/lib/graph/search.ts
write_and_commit(
    "apps/dashboard/src/lib/graph/search.ts",
    """import type { CytoscapeNodeData } from "../api/types";

export function matchNodeSearch(node: CytoscapeNodeData, query: string): boolean {
  if (!query || !query.trim()) return true;
  const q = query.trim().toLowerCase();

  if (node.id.toLowerCase().includes(q)) return true;
  if (node.label && node.label.toLowerCase().includes(q)) return true;
  if (node.cluster_id && node.cluster_id.toLowerCase().includes(q)) return true;
  if (node.username && node.username.toLowerCase().includes(q)) return true;

  return false;
}
""",
    "feat(graph): implement matchNodeSearch query filtering utility"
)

# 20. apps/dashboard/src/lib/graph/__tests__/search.test.ts
write_and_commit(
    "apps/dashboard/src/lib/graph/__tests__/search.test.ts",
    """import { describe, expect, it } from "vitest";
import { matchNodeSearch } from "../search";

describe("matchNodeSearch", () => {
  const node = {
    id: "acc_1001",
    label: "SuspiciousBot_42",
    username: "crypto_bot_daily",
    cluster_id: "cluster_alpha",
  };

  it("matches on ID", () => {
    expect(matchNodeSearch(node, "1001")).toBe(true);
    expect(matchNodeSearch(node, "9999")).toBe(false);
  });

  it("matches on label and username", () => {
    expect(matchNodeSearch(node, "Suspicious")).toBe(true);
    expect(matchNodeSearch(node, "crypto")).toBe(true);
  });

  it("matches on cluster ID", () => {
    expect(matchNodeSearch(node, "alpha")).toBe(true);
  });

  it("returns true for empty query", () => {
    expect(matchNodeSearch(node, "")).toBe(true);
    expect(matchNodeSearch(node, "   ")).toBe(true);
  });
});
""",
    "test(graph): test matchNodeSearch id, label, username, and cluster matching"
)

# 21. apps/dashboard/src/lib/hooks/use-graph-elements.ts
write_and_commit(
    "apps/dashboard/src/lib/hooks/use-graph-elements.ts",
    """import { useEffect, useState } from "react";
import { ENDPOINTS } from "../api/endpoints";
import type { CytoscapeGraphResponse } from "../api/types";

export interface UseGraphElementsOptions {
  maxNodes?: number;
  clusterId?: string;
  riskBand?: string;
  minScore?: number;
  token?: string;
}

export function useGraphElements(scanId: string, options: UseGraphElementsOptions = {}) {
  const [data, setData] = useState<CytoscapeGraphResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const { maxNodes = 500, clusterId, riskBand, minScore, token } = options;

  useEffect(() => {
    if (!scanId) return;

    let mounted = true;
    setLoading(true);
    setError(null);

    const url = new URL(ENDPOINTS.networks.graph(scanId));
    url.searchParams.set("max_nodes", String(maxNodes));
    if (clusterId) url.searchParams.set("cluster_id", clusterId);
    if (riskBand) url.searchParams.set("risk_band", riskBand);
    if (minScore !== undefined) url.searchParams.set("min_score", String(minScore));

    const headers: Record<string, string> = {};
    if (token) headers.Authorization = `Bearer ${token}`;

    fetch(url.toString(), { credentials: "omit", headers })
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to load graph elements: ${res.status}`);
        return res.json();
      })
      .then((json: CytoscapeGraphResponse) => {
        if (mounted) {
          setData(json);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (mounted) {
          setError(err);
          setLoading(false);
        }
      });

    return () => {
      mounted = false;
    };
  }, [scanId, maxNodes, clusterId, riskBand, minScore, token]);

  return { data, loading, error };
}
""",
    "feat(hooks): implement useGraphElements hook with query filtering and auth header"
)

# 22. apps/dashboard/src/lib/hooks/__tests__/use-graph-elements.test.ts
write_and_commit(
    "apps/dashboard/src/lib/hooks/__tests__/use-graph-elements.test.ts",
    """import { renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useGraphElements } from "../use-graph-elements";

describe("useGraphElements hook", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          scan_id: "scan_1",
          elements: { nodes: [{ data: { id: "a" } }], edges: [] },
          node_count: 1,
          edge_count: 0,
        }),
      })
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("fetches graph elements for scan id", async () => {
    const { result } = renderHook(() => useGraphElements("scan_1"));
    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data?.scan_id).toBe("scan_1");
    expect(result.current.data?.node_count).toBe(1);
    expect(result.current.error).toBeNull();
  });
});
""",
    "test(hooks): test useGraphElements fetch cycle and state updates"
)

# 23. apps/dashboard/src/lib/hooks/use-graph-clusters.ts
write_and_commit(
    "apps/dashboard/src/lib/hooks/use-graph-clusters.ts",
    """import { useEffect, useState } from "react";
import { ENDPOINTS } from "../api/endpoints";

export interface ClusterRecord {
  id: string;
  method: string;
  member_count: number;
  confidence: string;
  signal_strength: string;
  members: string[];
}

export function useGraphClusters(scanId: string, token?: string) {
  const [clusters, setClusters] = useState<ClusterRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!scanId) return;

    let mounted = true;
    setLoading(true);

    const headers: Record<string, string> = {};
    if (token) headers.Authorization = `Bearer ${token}`;

    fetch(ENDPOINTS.networks.clusters(scanId), { headers })
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to load clusters: ${res.status}`);
        return res.json();
      })
      .then((data) => {
        if (mounted) {
          setClusters(data.clusters || []);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (mounted) {
          setError(err);
          setLoading(false);
        }
      });

    return () => {
      mounted = false;
    };
  }, [scanId, token]);

  return { clusters, loading, error };
}
""",
    "feat(hooks): implement useGraphClusters hook for coordinated cluster records"
)

# 24. apps/dashboard/src/lib/hooks/__tests__/use-graph-clusters.test.ts
write_and_commit(
    "apps/dashboard/src/lib/hooks/__tests__/use-graph-clusters.test.ts",
    """import { renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useGraphClusters } from "../use-graph-clusters";

describe("useGraphClusters hook", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          scan_id: "scan_10",
          clusters: [
            { id: "c_1", method: "wcc", member_count: 5, confidence: "high", signal_strength: "strong", members: ["m1"] },
          ],
          total: 1,
        }),
      })
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("loads clusters list for scan", async () => {
    const { result } = renderHook(() => useGraphClusters("scan_10"));
    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.clusters).toHaveLength(1);
    expect(result.current.clusters[0].id).toBe("c_1");
  });
});
""",
    "test(hooks): test useGraphClusters fetch handling and state binding"
)

# 25. apps/dashboard/src/lib/hooks/use-node-neighbors.ts
write_and_commit(
    "apps/dashboard/src/lib/hooks/use-node-neighbors.ts",
    """import { useEffect, useState } from "react";
import { ENDPOINTS } from "../api/endpoints";
import type { NodeNeighborsResponse } from "../api/types";

export function useNodeNeighbors(
  scanId: string,
  nodeId: string | null,
  direction = "both",
  radius = 1,
  token?: string
) {
  const [data, setData] = useState<NodeNeighborsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!scanId || !nodeId) {
      setData(null);
      setLoading(false);
      return;
    }

    let mounted = true;
    setLoading(true);
    setError(null);

    const url = new URL(ENDPOINTS.networks.neighbors(scanId, nodeId));
    url.searchParams.set("direction", direction);
    url.searchParams.set("radius", String(radius));

    const headers: Record<string, string> = {};
    if (token) headers.Authorization = `Bearer ${token}`;

    fetch(url.toString(), { headers })
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to load neighbors: ${res.status}`);
        return res.json();
      })
      .then((json: NodeNeighborsResponse) => {
        if (mounted) {
          setData(json);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (mounted) {
          setError(err);
          setLoading(false);
        }
      });

    return () => {
      mounted = false;
    };
  }, [scanId, nodeId, direction, radius, token]);

  return { data, loading, error };
}
""",
    "feat(hooks): implement useNodeNeighbors hook for ego-neighborhood expansion"
)

# 26. apps/dashboard/src/lib/hooks/__tests__/use-node-neighbors.test.ts
write_and_commit(
    "apps/dashboard/src/lib/hooks/__tests__/use-node-neighbors.test.ts",
    """import { renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useNodeNeighbors } from "../use-node-neighbors";

describe("useNodeNeighbors hook", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          scan_id: "scan_1",
          center_node_id: "acc_1",
          direction: "both",
          radius: 1,
          neighbors: [
            { node_id: "acc_2", direction: "inbound", relationship_type: "follower", risk_score: 0.88, risk_band: "high" },
          ],
          total: 1,
        }),
      })
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("fetches neighbors when focal nodeId is provided", async () => {
    const { result } = renderHook(() => useNodeNeighbors("scan_1", "acc_1"));
    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data?.neighbors).toHaveLength(1);
    expect(result.current.data?.center_node_id).toBe("acc_1");
  });

  it("does not fetch when nodeId is null", () => {
    const { result } = renderHook(() => useNodeNeighbors("scan_1", null));
    expect(result.current.loading).toBe(false);
    expect(result.current.data).toBeNull();
  });
});
""",
    "test(hooks): test useNodeNeighbors null check and neighbor response dispatch"
)

# 27. apps/dashboard/src/lib/hooks/use-graph-metrics.ts
write_and_commit(
    "apps/dashboard/src/lib/hooks/use-graph-metrics.ts",
    """import { useEffect, useState } from "react";
import { ENDPOINTS } from "../api/endpoints";
import type { GraphMetricsResponse } from "../api/types";

export function useGraphMetrics(scanId: string, token?: string) {
  const [metrics, setMetrics] = useState<GraphMetricsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!scanId) return;

    let mounted = true;
    setLoading(true);

    const headers: Record<string, string> = {};
    if (token) headers.Authorization = `Bearer ${token}`;

    fetch(ENDPOINTS.networks.metrics(scanId), { headers })
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to load network metrics: ${res.status}`);
        return res.json();
      })
      .then((data: GraphMetricsResponse) => {
        if (mounted) {
          setMetrics(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (mounted) {
          setError(err);
          setLoading(false);
        }
      });

    return () => {
      mounted = false;
    };
  }, [scanId, token]);

  return { metrics, loading, error };
}
""",
    "feat(hooks): implement useGraphMetrics hook for macroscopic graph topology measures"
)

# 28. apps/dashboard/src/lib/hooks/__tests__/use-graph-metrics.test.ts
write_and_commit(
    "apps/dashboard/src/lib/hooks/__tests__/use-graph-metrics.test.ts",
    """import { renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useGraphMetrics } from "../use-graph-metrics";

describe("useGraphMetrics hook", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          scan_id: "scan_1",
          node_count: 50,
          edge_count: 100,
          density: 0.04,
          reciprocity: 0.15,
          weakly_connected_components: 3,
          strongly_connected_components: 10,
          avg_in_degree: 2.0,
          avg_out_degree: 2.0,
        }),
      })
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("fetches topology metrics", async () => {
    const { result } = renderHook(() => useGraphMetrics("scan_1"));
    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.metrics?.node_count).toBe(50);
    expect(result.current.metrics?.density).toBe(0.04);
  });
});
""",
    "test(hooks): test useGraphMetrics fetch cycle and state updates"
)

# 29. tests/graph/test_graph_hulls.py
write_and_commit(
    "tests/graph/test_graph_hulls.py",
    """from __future__ import annotations

import networkx as nx

from sbh.graph.algorithms import calculate_cluster_cohesion, detect_connected_communities


def test_cluster_community_hull_cohesion() -> None:
    g = nx.DiGraph()
    # Fully connected 3-clique
    nodes = ["a", "b", "c"]
    for u in nodes:
        for v in nodes:
            if u != v:
                g.add_edge(u, v)

    cohesion = calculate_cluster_cohesion(g, nodes)
    assert cohesion == 1.0

    comms = detect_connected_communities(g)
    assert len(comms) == 1
    assert len(comms[0]) == 3
""",
    "test(graph): test clique cohesion and connected community properties"
)

# 30. tests/graph/test_graph_search_filter.py
write_and_commit(
    "tests/graph/test_graph_search_filter.py",
    """from __future__ import annotations

import networkx as nx

from sbh.graph.ego import extract_ego_subgraph


def test_ego_subgraph_filter_preserves_attributes() -> None:
    g = nx.DiGraph()
    g.add_node("target", score=0.88, band="high")
    g.add_node("peer", score=0.44, band="medium")
    g.add_edge("target", "peer", relationship_type="following")

    sub = extract_ego_subgraph(g, "target", radius=1, direction="out")
    assert sub.nodes["target"]["score"] == 0.88
    assert sub.nodes["peer"]["band"] == "medium"
    assert sub.edges[("target", "peer")]["relationship_type"] == "following"
""",
    "test(graph): test attribute preservation in extracted ego subgraph"
)

# 31. docs/status/day-06/04-graph-tokens-and-stylesheet-delivered.md
write_and_commit(
    "docs/status/day-06/04-graph-tokens-and-stylesheet-delivered.md",
    """# Day 6 Status 04: Graph Tokens and Cytoscape Stylesheet Delivered

Delivered graph visualization foundation:
- `GRAPH_NODE_COLORS`: Five risk band color mappings with high contrast.
- `GRAPH_NODE_SIZES`: Configurable node dimensions for regular and focal nodes.
- `CLUSTER_HULL_PALETTE`: Distinguishable hull polygon tints for botnet clusters.
- `getCytoscapeStylesheet`: Production stylesheet with bezier curved edges, arrowheads, and interactive hover/highlight/dim states.
""",
    "docs(status): log graph tokens and stylesheet delivery in report 04"
)

# 32. docs/status/day-06/05-cytoscape-layouts-and-transforms-delivered.md
write_and_commit(
    "docs/status/day-06/05-cytoscape-layouts-and-transforms-delivered.md",
    """# Day 6 Status 05: Cytoscape Layouts and Transforms Delivered

Delivered layout engine and graph transformers:
- Layout presets: Force-directed `cose`, Concentric risk level ordering, Circle, Breadthfirst directed hierarchy, Grid.
- Filter helpers: `filterCytoscapeElements` supporting threshold, risk band, cluster, and query.
- Export utilities: `exportGraphPng` high-resolution canvas snapshot and `exportGraphJson`.
""",
    "docs(status): log cytoscape layout engine and element transforms in report 05"
)

# 33. docs/status/day-06/06-graph-hooks-and-expansion-delivered.md
write_and_commit(
    "docs/status/day-06/06-graph-hooks-and-expansion-delivered.md",
    """# Day 6 Status 06: Graph Hooks and Neighbor Expansion Delivered

Delivered React hooks for graph explorer:
- `useGraphElements`: Load Cytoscape element payload with query params.
- `useGraphClusters`: Coordinated bot cluster listings.
- `useNodeNeighbors`: 1/2-hop ego expansion around focal nodes.
- `useGraphMetrics`: Macroscopic graph topology statistics.
""",
    "docs(status): log graph data hooks and ego-expansion integration in report 06"
)

# 34. apps/dashboard/src/lib/graph/highlight.ts
write_and_commit(
    "apps/dashboard/src/lib/graph/highlight.ts",
    """import type { Core } from "cytoscape";

export function highlightNodeAndNeighbors(cy: Core, nodeId: string | null): void {
  if (!cy) return;

  cy.batch(() => {
    if (!nodeId) {
      cy.elements().removeClass("highlighted dimmed");
      return;
    }

    const focalNode = cy.$id(nodeId);
    if (!focalNode.length) return;

    const neighborhood = focalNode.neighborhood().add(focalNode);
    cy.elements().difference(neighborhood).addClass("dimmed").removeClass("highlighted");
    neighborhood.addClass("highlighted").removeClass("dimmed");
  });
}
""",
    "feat(graph): implement highlightNodeAndNeighbors for focused visual inspection"
)

# 35. apps/dashboard/src/lib/graph/__tests__/highlight.test.ts
write_and_commit(
    "apps/dashboard/src/lib/graph/__tests__/highlight.test.ts",
    """import { describe, expect, it, vi } from "vitest";
import { highlightNodeAndNeighbors } from "../highlight";

describe("highlightNodeAndNeighbors", () => {
  it("clears highlights when nodeId is null", () => {
    const mockElements = {
      removeClass: vi.fn(),
    };
    const mockCy: any = {
      batch: (fn: any) => fn(),
      elements: () => mockElements,
    };

    highlightNodeAndNeighbors(mockCy, null);
    expect(mockElements.removeClass).toHaveBeenCalledWith("highlighted dimmed");
  });

  it("highlights focal node and neighborhood while dimming others", () => {
    const mockNeighborhood = {
      addClass: vi.fn().mockReturnThis(),
      removeClass: vi.fn().mockReturnThis(),
    };
    const mockFocal = {
      length: 1,
      neighborhood: () => ({
        add: () => mockNeighborhood,
      }),
    };
    const mockNonNeighborhood = {
      addClass: vi.fn().mockReturnThis(),
      removeClass: vi.fn().mockReturnThis(),
    };
    const mockAll = {
      difference: () => mockNonNeighborhood,
    };

    const mockCy: any = {
      batch: (fn: any) => fn(),
      $id: vi.fn().mockReturnValue(mockFocal),
      elements: () => mockAll,
    };

    highlightNodeAndNeighbors(mockCy, "focal_node");
    expect(mockCy.$id).toHaveBeenCalledWith("focal_node");
    expect(mockNeighborhood.addClass).toHaveBeenCalledWith("highlighted");
    expect(mockNonNeighborhood.addClass).toHaveBeenCalledWith("dimmed");
  });
});
""",
    "test(graph): test highlightNodeAndNeighbors batch element class toggling"
)

print("Batch 2 completed 35 commits successfully.")
