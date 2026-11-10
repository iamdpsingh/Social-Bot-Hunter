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
