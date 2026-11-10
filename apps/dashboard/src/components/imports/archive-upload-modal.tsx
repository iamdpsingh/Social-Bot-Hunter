"use client";

import React, { useState, useRef } from "react";
import { UploadCloud, FileArchive, CheckCircle2, AlertTriangle, Loader2, X } from "lucide-react";
import { Modal } from "../ui/modal";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";

export interface ArchiveUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (extractedPath: string, format: string, fileCount: number) => void;
}

export interface ExtractionSummary {
  format: string;
  fileCount: number;
  uncompressedBytes: number;
  platformDetected: string | null;
  extractedPath: string;
}

export function ArchiveUploadModal({ isOpen, onClose, onSuccess }: ArchiveUploadModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [status, setStatus] = useState<"idle" | "uploading" | "extracted" | "error">("idle");
  const [progress, setProgress] = useState(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [summary, setSummary] = useState<ExtractionSummary | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const validateAndSetFile = (selectedFile: File) => {
    setErrorMessage(null);
    const maxSizeBytes = 150 * 1024 * 1024; // 150 MB
    if (selectedFile.size > maxSizeBytes) {
      setErrorMessage(`Archive exceeds client size limit of 150MB (${(selectedFile.size / 1024 / 1024).toFixed(1)}MB)`);
      setStatus("error");
      return;
    }
    const validExtensions = [".zip", ".tar.gz", ".tgz", ".tar", ".ndjson", ".jsonl", ".csv"];
    const nameLower = selectedFile.name.toLowerCase();
    const hasValidExt = validExtensions.some(ext => nameLower.endsWith(ext));
    if (!hasValidExt) {
      setErrorMessage("Unsupported file type. Please select .zip, .tar.gz, .ndjson, or .csv");
      setStatus("error");
      return;
    }
    setFile(selectedFile);
    setStatus("idle");
  };

  const handleUpload = async () => {
    if (!file) return;
    setStatus("uploading");
    setProgress(20);
    try {
      const formData = new FormData();
      formData.append("file", file);
      setProgress(50);
      const resp = await fetch("/api/v1/imports/archive", {
        method: "POST",
        body: formData,
      });
      setProgress(85);
      if (!resp.ok) {
        const errData = await resp.json().catch(() => ({}));
        const msg = errData?.detail?.message || errData?.detail || `Upload failed with HTTP ${resp.status}`;
        throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
      }
      const data = await resp.json();
      setProgress(100);
      setStatus("extracted");
      setSummary({
        format: data.archive_format,
        fileCount: data.file_count,
        uncompressedBytes: data.uncompressed_bytes,
        platformDetected: data.platform_detected,
        extractedPath: data.extracted_path,
      });
      if (onSuccess) {
        onSuccess(data.extracted_path, data.archive_format, data.file_count);
      }
    } catch (err: any) {
      setStatus("error");
      setErrorMessage(err.message || "Failed to unpack and inspect archive");
    }
  };

  const formatBadgeVariant = (fmt: string): "default" | "secondary" | "success" | "warning" => {
    if (fmt === "twitter_archive") return "default";
    if (fmt === "ndjson" || fmt === "csv") return "success";
    if (fmt === "generic_json") return "secondary";
    return "warning";
  };

  const handleReset = () => {
    setFile(null);
    setStatus("idle");
    setProgress(0);
    setErrorMessage(null);
    setSummary(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  const handleClose = () => {
    handleReset();
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Dataset Archive Ingestion & Security Inspection">
      <div className="space-y-4" data-testid="archive-upload-modal-content">
        {/* Dropzone */}
        {status === "idle" && (
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => inputRef.current?.click()}
            role="button"
            tabIndex={0}
            aria-label="Upload social dataset archive"
            onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") inputRef.current?.click(); }}
            className={`flex flex-col items-center justify-center p-8 border-2 border-dashed rounded-xl cursor-pointer transition-colors ${
              isDragging ? "border-primary bg-primary/10" : "border-white/10 hover:border-white/20 bg-white/5"
            }`}
            data-testid="archive-dropzone"
          >
            <input
              ref={inputRef}
              type="file"
              className="hidden"
              accept=".zip,.tar.gz,.tgz,.tar,.ndjson,.jsonl,.csv"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) validateAndSetFile(e.target.files[0]);
              }}
              data-testid="archive-file-input"
            />
            <UploadCloud className="h-10 w-10 text-muted-foreground mb-3" />
            <p className="text-sm font-medium text-foreground">
              {file ? file.name : "Drag & drop your archive here, or click to browse"}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Supported: Twitter Archive (.zip), NDJSON streams, CSV manifests (Max 150MB)
            </p>
          </div>
        )}

        {/* Progress */}
        {status === "uploading" && (
          <div className="p-6 space-y-3 bg-white/5 rounded-xl border border-white/10" data-testid="upload-progress-container">
            <div className="flex items-center justify-between text-xs">
              <span className="flex items-center gap-2"><Loader2 className="h-4 w-4 animate-spin text-primary" /> Inspecting & unpacking archive...</span>
              <span className="font-semibold">{progress}%</span>
            </div>
            <div className="w-full bg-white/10 h-2 rounded-full overflow-hidden">
              <div className="bg-primary h-full transition-all duration-300" style={{ width: `${progress}%` }} />
            </div>
          </div>
        )}

        {/* Extracted Summary */}
        {status === "extracted" && summary && (
          <div className="p-5 space-y-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl" data-testid="extracted-summary">
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-2 text-sm font-semibold text-emerald-400">
                <CheckCircle2 className="h-5 w-5" /> Archive Verified & Unpacked
              </span>
              <Badge variant={formatBadgeVariant(summary.format)}>{summary.format}</Badge>
            </div>
            <div className="grid grid-cols-3 gap-2 text-xs pt-2 border-t border-emerald-500/20">
              <div><span className="text-muted-foreground">Files:</span> <span className="font-semibold text-foreground">{summary.fileCount}</span></div>
              <div><span className="text-muted-foreground">Size:</span> <span className="font-semibold text-foreground">{(summary.uncompressedBytes / 1024).toFixed(1)} KB</span></div>
              <div><span className="text-muted-foreground">Platform:</span> <span className="font-semibold text-foreground capitalize">{summary.platformDetected || "Generic"}</span></div>
            </div>
          </div>
        )}

        {/* Error Banner */}
        {errorMessage && (
          <div className="flex items-start gap-3 p-4 bg-destructive/15 border border-destructive/30 rounded-xl text-xs text-destructive-foreground" data-testid="error-banner">
            <AlertTriangle className="h-4 w-4 text-destructive shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="font-semibold">Security / Validation Error</p>
              <p className="text-muted-foreground mt-0.5">{errorMessage}</p>
            </div>
            <button onClick={() => setErrorMessage(null)} className="text-muted-foreground hover:text-foreground" aria-label="Dismiss error">
              <X className="h-4 w-4" />
            </button>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center justify-end gap-2 pt-2 border-t border-white/5">
          <Button variant="ghost" size="sm" onClick={handleClose}>Close</Button>
          {status === "idle" && (
            <Button size="sm" disabled={!file} onClick={handleUpload} data-testid="start-upload-button">
              Inspect & Ingest
            </Button>
          )}
          {status === "extracted" && (
            <Button size="sm" onClick={handleReset}>Upload Another</Button>
          )}
        </div>
      </div>
    </Modal>
  );
}
