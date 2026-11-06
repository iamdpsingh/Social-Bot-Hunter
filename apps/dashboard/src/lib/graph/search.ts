import type { CytoscapeNodeData } from "../api/types";

export function matchNodeSearch(node: CytoscapeNodeData, query: string): boolean {
  if (!query || !query.trim()) return true;
  const q = query.trim().toLowerCase();

  if (node.id.toLowerCase().includes(q)) return true;
  if (node.label && node.label.toLowerCase().includes(q)) return true;
  if (node.cluster_id && node.cluster_id.toLowerCase().includes(q)) return true;
  if (node.username && node.username.toLowerCase().includes(q)) return true;

  return false;
}
