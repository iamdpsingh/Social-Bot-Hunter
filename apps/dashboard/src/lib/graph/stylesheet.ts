import type { StylesheetStyle } from "cytoscape";
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
