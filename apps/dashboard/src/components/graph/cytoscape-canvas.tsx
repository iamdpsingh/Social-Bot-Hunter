"use client";

import React, { useEffect, useRef } from "react";
import cytoscape, { type Core, type EventObject } from "cytoscape";
import { getCytoscapeStylesheet } from "../../lib/graph/stylesheet";
import { getLayoutOptions } from "../../lib/graph/layouts";
import type { CytoscapeGraphElements, CytoscapeNodeData } from "../../lib/api/types";
import type { LayoutPresetId } from "../../tokens/graph";

export interface CytoscapeCanvasProps {
  elements: CytoscapeGraphElements;
  layoutPreset?: LayoutPresetId;
  selectedNodeId?: string | null;
  onSelectNode?: (nodeId: string | null, nodeData?: CytoscapeNodeData | null) => void;
  onInitCy?: (cy: Core) => void;
  className?: string;
}

export function CytoscapeCanvas({
  elements,
  layoutPreset = "cose",
  selectedNodeId,
  onSelectNode,
  onInitCy,
  className = "w-full h-full min-h-[500px]",
}: CytoscapeCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    let cyInstance: Core | null = null;
    try {
      cyInstance = cytoscape({
        container: containerRef.current,
        elements: [
          ...elements.nodes.map((n) => ({ group: "nodes" as const, data: n.data })),
          ...elements.edges.map((e) => ({ group: "edges" as const, data: e.data })),
        ],
        style: getCytoscapeStylesheet(),
        layout: getLayoutOptions(layoutPreset),
        wheelSensitivity: 0.2,
        minZoom: 0.1,
        maxZoom: 5.0,
      });

      cyRef.current = cyInstance;
      if (onInitCy) onInitCy(cyInstance);

      cyInstance.on("tap", "node", (evt: EventObject) => {
        const node = evt.target;
        onSelectNode?.(node.id(), node.data());
      });

      cyInstance.on("tap", (evt: EventObject) => {
        if (evt.target === cyInstance) {
          onSelectNode?.(null, null);
        }
      });
    } catch {
      // Graceful fallback for non-canvas environments (JSDOM/SSR)
    }

    return () => {
      try {
        cyInstance?.destroy();
      } catch {
        // ignore cleanup errors in testing
      }
    };
  }, [elements, layoutPreset]);

  // Synchronize selection state with cytoscape node selection
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    try {
      cy.batch(() => {
        cy.nodes().unselect();
        if (selectedNodeId) {
          cy.$id(selectedNodeId).select();
        }
      });
    } catch {
      // ignore in mock environments
    }
  }, [selectedNodeId]);

  return (
    <div
      ref={containerRef}
      data-testid="cytoscape-canvas"
      className={`relative bg-slate-950/80 rounded-lg overflow-hidden border border-slate-800 ${className}`}
      aria-label="Interactive directed graph canvas"
      role="region"
    />
  );
}
