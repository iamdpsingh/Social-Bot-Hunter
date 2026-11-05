import React, { useState } from "react";
import { FileText, Download, Code } from "lucide-react";
import { Modal } from "../ui/modal";
import { Button } from "../ui/button";
import { useInvestigationExport } from "../../lib/hooks/use-investigation-export";

export interface ExportDialogProps {
  isOpen: boolean;
  onClose: () => void;
  scanId: string;
  isSynthetic?: boolean;
}

export function ExportDialog({
  isOpen,
  onClose,
  scanId,
  isSynthetic = false,
}: ExportDialogProps) {
  const { downloadCsv, downloadJson, isExporting } = useInvestigationExport(scanId);
  const [format, setFormat] = useState<"csv" | "json">("csv");

  const handleExport = async () => {
    if (format === "csv") {
      await downloadCsv();
    } else {
      await downloadJson();
    }
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Export Investigation Results"
      description="Download authorized evidence records and risk assessment calculations."
    >
      <div className="space-y-4 pt-2">
        {isSynthetic && (
          <div className="rounded border border-amber-500/20 bg-amber-500/10 p-3 text-xs text-amber-300">
            Exported data originates from a synthetic benchmark dataset. Ground truth claims are labeled.
          </div>
        )}

        <div className="grid grid-cols-2 gap-3">
          <button
            type="button"
            onClick={() => setFormat("csv")}
            className={`flex flex-col items-center justify-center p-4 rounded-lg border text-center transition-colors ${
              format === "csv"
                ? "border-primary bg-primary/10 text-primary"
                : "border-white/5 bg-white/5 text-muted-foreground hover:bg-white/10"
            }`}
          >
            <FileText className="h-6 w-6 mb-2" />
            <span className="font-semibold text-xs text-foreground">RFC 4180 CSV</span>
            <span className="text-[10px] text-muted-foreground mt-0.5">Spreadsheet ready table</span>
          </button>

          <button
            type="button"
            onClick={() => setFormat("json")}
            className={`flex flex-col items-center justify-center p-4 rounded-lg border text-center transition-colors ${
              format === "json"
                ? "border-primary bg-primary/10 text-primary"
                : "border-white/5 bg-white/5 text-muted-foreground hover:bg-white/10"
            }`}
          >
            <Code className="h-6 w-6 mb-2" />
            <span className="font-semibold text-xs text-foreground">JSON Evidence Bundle</span>
            <span className="text-[10px] text-muted-foreground mt-0.5">Full metadata and clusters</span>
          </button>
        </div>

        <div className="flex items-center justify-end gap-3 pt-3 border-t border-white/5">
          <Button type="button" variant="ghost" onClick={onClose} disabled={isExporting}>
            Cancel
          </Button>
          <Button onClick={handleExport} isLoading={isExporting} className="gap-2">
            <Download className="h-4 w-4" /> Download {format.toUpperCase()}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
