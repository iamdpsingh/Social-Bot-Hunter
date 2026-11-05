import React from "react";
import { ShieldAlert, Info } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/card";
import { formatLimitationNotice } from "../../lib/utils/limitations";

export interface LimitationsCardProps {
  limitations?: string[];
  coveragePct?: number;
}

export function LimitationsCard({ limitations = [], coveragePct = 100 }: LimitationsCardProps) {
  return (
    <Card className="border-amber-500/20 bg-amber-500/5">
      <CardHeader className="py-4 px-6 flex flex-row items-center justify-between">
        <div className="flex items-center gap-2 text-amber-400">
          <ShieldAlert className="h-4 w-4" />
          <CardTitle className="text-sm font-semibold text-amber-400">
            Data Limitations & Unobservable Coverage
          </CardTitle>
        </div>
        <span className="text-xs font-mono font-semibold text-amber-300">
          Coverage: {coveragePct}%
        </span>
      </CardHeader>

      <CardContent className="px-6 pb-6 pt-0 space-y-2 text-xs">
        {limitations.length === 0 ? (
          <p className="text-muted-foreground flex items-center gap-2">
            <Info className="h-3.5 w-3.5" /> Full observable feature coverage achieved. No active platform restrictions.
          </p>
        ) : (
          <ul className="space-y-2">
            {limitations.map((lim, idx) => {
              const notice = formatLimitationNotice(lim);
              return (
                <li key={idx} className="flex flex-col gap-0.5 bg-amber-500/10 p-2.5 rounded border border-amber-500/20">
                  <span className="font-semibold text-amber-200">{notice.title}</span>
                  <span className="text-amber-300/80 text-[11px]">{notice.explanation}</span>
                </li>
              );
            })}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
