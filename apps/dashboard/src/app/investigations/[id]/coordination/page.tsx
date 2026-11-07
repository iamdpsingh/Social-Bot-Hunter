import React from "react";
import { CoordinationClient } from "./coordination-client";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function InvestigationCoordinationPage({ params }: PageProps) {
  const { id } = await params;
  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <CoordinationClient scanId={id} />
    </div>
  );
}
