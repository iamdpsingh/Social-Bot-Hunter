import React from "react";
import { ArrowDownLeft, ArrowUpRight } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/card";
import type { AccountNeighborhoodEdge, AccountNeighborhoodResponse } from "../../lib/api/types";

export interface AccountNeighborhoodViewerProps {
  inEdges?: AccountNeighborhoodEdge[];
  outEdges?: AccountNeighborhoodEdge[];
  currentAccountId?: string;
  neighborhood?: AccountNeighborhoodResponse | any;
}

export function AccountNeighborhoodViewer({
  inEdges: propInEdges,
  outEdges: propOutEdges,
  currentAccountId,
  neighborhood,
}: AccountNeighborhoodViewerProps) {
  const inEdges = propInEdges ?? neighborhood?.incoming ?? neighborhood?.in_edges ?? [];
  const outEdges = propOutEdges ?? neighborhood?.outgoing ?? neighborhood?.out_edges ?? [];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <Card className="border-white/5 bg-slate-900/40">
        <CardHeader className="py-3 px-4 flex flex-row items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-semibold text-foreground">
            <ArrowDownLeft className="h-4 w-4 text-blue-400" />
            <CardTitle className="text-xs font-semibold">Inbound Followers</CardTitle>
          </div>
          <span className="font-mono text-xs text-muted-foreground">{inEdges.length}</span>
        </CardHeader>
        <CardContent className="px-4 pb-4 pt-0">
          {inEdges.length === 0 ? (
            <p className="text-xs text-muted-foreground py-2">No observed inbound edges</p>
          ) : (
            <ul className="divide-y divide-white/5 text-xs font-mono">
              {inEdges.slice(0, 10).map((edge: any, idx: number) => (
                <li key={idx} className="py-1.5 text-muted-foreground truncate">
                  {edge.source || edge.source_id || "edge"}
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <Card className="border-white/5 bg-slate-900/40">
        <CardHeader className="py-3 px-4 flex flex-row items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-semibold text-foreground">
            <ArrowUpRight className="h-4 w-4 text-purple-400" />
            <CardTitle className="text-xs font-semibold">Outbound Following</CardTitle>
          </div>
          <span className="font-mono text-xs text-muted-foreground">{outEdges.length}</span>
        </CardHeader>
        <CardContent className="px-4 pb-4 pt-0">
          {outEdges.length === 0 ? (
            <p className="text-xs text-muted-foreground py-2">No observed outbound edges</p>
          ) : (
            <ul className="divide-y divide-white/5 text-xs font-mono">
              {outEdges.slice(0, 10).map((edge: any, idx: number) => (
                <li key={idx} className="py-1.5 text-muted-foreground truncate">
                  {edge.target || edge.target_id || "edge"}
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
