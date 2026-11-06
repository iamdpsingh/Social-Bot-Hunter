import type { Core } from "cytoscape";

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
