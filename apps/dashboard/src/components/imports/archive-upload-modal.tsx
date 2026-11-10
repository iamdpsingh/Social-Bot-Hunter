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
