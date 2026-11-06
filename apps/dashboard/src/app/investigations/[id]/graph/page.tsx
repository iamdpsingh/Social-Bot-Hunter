import React from "react";
import { GraphPageClient } from "../../../../components/graph/graph-page-client";

interface PageProps {
  params: {
    id: string;
  };
}

export default function InvestigationGraphPage({ params }: PageProps) {
  return <GraphPageClient scanId={params.id} />;
}
