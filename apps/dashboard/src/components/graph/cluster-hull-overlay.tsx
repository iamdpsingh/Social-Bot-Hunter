"use client";

import React from "react";
import { CLUSTER_HULL_PALETTE } from "../../tokens/graph";
import type { Point } from "../../lib/graph/cluster-hull";

export interface ClusterHullPolygon {
  clusterId: string;
  points: Point[];
}

export interface ClusterHullOverlayProps {
  hulls: ClusterHullPolygon[];
  visible?: boolean;
}

export function ClusterHullOverlay({ hulls, visible = true }: ClusterHullOverlayProps) {
  if (!visible || hulls.length === 0) return null;

  return (
    <svg
      data-testid="cluster-hull-overlay"
      className="absolute inset-0 pointer-events-none w-full h-full z-10"
      aria-hidden="true"
    >
      {hulls.map((hull, idx) => {
        if (hull.points.length < 3) return null;
        const color = CLUSTER_HULL_PALETTE[idx % CLUSTER_HULL_PALETTE.length];
        const pointsStr = hull.points.map((p) => `${p.x},${p.y}`).join(" ");

        return (
          <polygon
            key={hull.clusterId}
            points={pointsStr}
            fill={color}
            stroke={color.replace("0.15", "0.5")}
            strokeWidth="2"
            strokeDasharray="4 2"
          />
        );
      })}
    </svg>
  );
}
