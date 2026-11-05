import React from "react";
import { Card, CardContent } from "../ui/card";

export interface FollowerRatioGaugeProps {
  followers: number;
  following: number;
}

export function FollowerRatioGauge({ followers, following }: FollowerRatioGaugeProps) {
  const ratio = following === 0 ? followers : Number((followers / following).toFixed(2));
  const isAnomalous = following > 500 && ratio < 0.1;

  return (
    <Card className="border-white/5 bg-slate-900/40">
      <CardContent className="p-4 flex items-center justify-between text-xs">
        <div>
          <span className="text-muted-foreground uppercase tracking-wider text-[10px] font-semibold block">
            Follower-to-Following Ratio
          </span>
          <span className="font-mono text-lg font-bold text-foreground">
            {ratio}x
          </span>
        </div>

        <div className="text-right">
          <span className={`inline-flex rounded px-2 py-0.5 text-[10px] font-semibold ${
            isAnomalous
              ? "bg-red-500/10 text-red-400 border border-red-500/20"
              : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
          }`}>
            {isAnomalous ? "Anomalous Ratio" : "Normal Distribution"}
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
