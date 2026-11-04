import React from "react";
import { ShieldAlert, Plus, Upload } from "lucide-react";
import { Card, CardContent } from "../ui/card";
import { Button } from "../ui/button";

export function EmptyInvestigationState({ onActionClick }: { onActionClick?: () => void }) {
  return (
    <Card className="border-dashed border-white/10 bg-slate-900/30">
      <CardContent className="flex flex-col items-center justify-center py-12 px-4 text-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary border border-primary/20 mb-4">
          <ShieldAlert className="h-6 w-6" />
        </div>
        <h3 className="text-base font-semibold text-foreground">No Active Investigations</h3>
        <p className="text-xs text-muted-foreground mt-1 max-w-sm">
          Start a new scan by supplying a social media profile handle, or import a synthetic demo dataset to evaluate coordinated networks.
        </p>
        <div className="flex items-center gap-3 mt-6">
          {onActionClick && (
            <Button size="sm" onClick={onActionClick} className="gap-1.5">
              <Plus className="h-4 w-4" /> Start Scan
            </Button>
          )}
          <a
            href="http://localhost:8080/docs"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 h-9 px-4 py-2 rounded-md border border-input text-xs font-medium text-muted-foreground hover:bg-white/5 hover:text-foreground transition-colors"
          >
            <Upload className="h-4 w-4" /> Import Dataset
          </a>
        </div>
      </CardContent>
    </Card>
  );
}
