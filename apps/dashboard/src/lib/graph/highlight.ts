import type { Core } from "cytoscape";

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
