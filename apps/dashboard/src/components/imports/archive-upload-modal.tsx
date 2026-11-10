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
