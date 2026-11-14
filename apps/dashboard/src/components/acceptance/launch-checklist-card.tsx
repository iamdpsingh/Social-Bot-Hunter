import React from 'react';
import { CheckCircle2, Calendar } from 'lucide-react';
import { LaunchChecklistItem } from '../../lib/types/acceptance';

interface Props {
  items: LaunchChecklistItem[];
}

export function LaunchChecklistCard({ items }: Props) {
  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
      <div className="flex items-center gap-3 pb-4 border-b border-border">
        <Calendar className="h-6 w-6 text-primary" />
        <div>
          <h2 className="text-lg font-bold text-foreground">14-Day Delivery Checklist</h2>
          <p className="text-xs text-muted-foreground">Milestones and commit cadence verification</p>
        </div>
      </div>

      <div className="divide-y divide-border mt-3">
        {items.map((item) => (
          <div key={item.dayNumber} className="py-2.5 flex items-center justify-between text-sm">
            <div className="flex items-center gap-3">
              <CheckCircle2 className="h-4 w-4 text-emerald-500" />
              <span className="font-medium text-foreground">Day {item.dayNumber}: {item.title}</span>
            </div>
            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              <span className="font-mono bg-muted px-2 py-0.5 rounded">{item.commitsCount}+ commits</span>
              <span>{item.signoffDate}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
