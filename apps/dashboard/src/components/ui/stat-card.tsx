import React from "react";
import { LucideIcon } from "lucide-react";
import { Card, CardContent } from "./card";
import { cn } from "../../lib/utils";

export interface StatCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon?: LucideIcon;
  trend?: {
    value: string;
    isPositive?: boolean;
  };
  coveragePct?: number;
  className?: string;
}

export function StatCard({
  title,
  value,
  description,
  icon: Icon,
  trend,
  coveragePct,
  className,
}: StatCardProps) {
  return (
    <Card className={cn("overflow-hidden", className)}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">{title}</p>
          {Icon && (
            <div className="rounded-lg bg-primary/10 p-2 text-primary">
              <Icon className="h-4 w-4" />
            </div>
          )}
        </div>
        <div className="mt-2 flex items-baseline gap-2">
          <span className="text-2xl font-bold tracking-tight text-foreground">{value}</span>
          {trend && (
            <span
              className={cn(
                "text-xs font-medium",
                trend.isPositive ? "text-emerald-400" : "text-amber-400"
              )}
            >
              {trend.value}
            </span>
          )}
        </div>
        {(description || coveragePct !== undefined) && (
          <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
            {description && <span>{description}</span>}
            {coveragePct !== undefined && (
              <span className="font-mono text-[10px] bg-white/5 px-1.5 py-0.5 rounded">
                {coveragePct}% coverage
              </span>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
