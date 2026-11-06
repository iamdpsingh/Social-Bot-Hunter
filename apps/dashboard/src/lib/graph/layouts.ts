import type { LayoutOptions } from "cytoscape";
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
