import React from "react";
import { Clock } from "lucide-react";
import { Card, CardContent } from "../ui/card";

export interface TimelineSnapshotProps {
  observedAt: string;
  source: string;
  followers: number;
  following: number;
}

export function TimelineSnapshot({
  observedAt,
  source,
  followers,
  following,
}: TimelineSnapshotProps) {
  return (
    <Card className="border-white/5 bg-white/5">
      <CardContent className="p-4 flex items-center justify-between text-xs">
        <div className="flex items-center gap-3">
          <Clock className="h-4 w-4 text-primary" />
          <div>
            <span className="font-semibold text-foreground">Snapshot Observed</span>
            <span className="text-muted-foreground ml-2 text-[11px]">
              {new Date(observedAt).toLocaleString()}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-4 font-mono text-xs">
          <span>{followers.toLocaleString()} followers</span>
          <span>{following.toLocaleString()} following</span>
          <span className="text-[10px] bg-white/5 px-2 py-0.5 rounded text-muted-foreground">{source}</span>
        </div>
      </CardContent>
    </Card>
  );
}
