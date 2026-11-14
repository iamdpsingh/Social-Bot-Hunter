# Social Bot Hunter - System Architecture & Engineering Topology

This document describes the high-level architecture, module decomposition, and data flow of Social Bot Hunter v1.0.0.

## 1. System Topology Overview

```mermaid
graph TD
    User["Security Analyst / Investigator"] --> UI["Next.js 14 Dashboard (:3000)"]
    UI --> API["FastAPI REST Service (:8000)"]
    API --> Auth["JWT & Role-Based Access Control"]
    API --> Middleware["Rate Limiter & Trace Correlation"]

    API --> Storage["Dual Backend Storage (SQLite / PostgreSQL)"]
    API --> Worker["Local Process Queue Worker"]

    Worker --> Ingestion["Adapter Ingestion Engine"]
    Ingestion --> Twitter["Twitter / X Adapter"]
    Ingestion --> Bluesky["Bluesky AT Protocol Adapter"]
    Ingestion --> Mastodon["Mastodon / Fediverse Adapter"]
    Ingestion --> Reddit["Reddit API Adapter"]
    Ingestion --> YouTube["YouTube Data v3 Adapter"]

    Worker --> Detection["Detection Core"]
    Detection --> Heuristic["Heuristic Rule Engine (rules-v1)"]
    Detection --> ML["Calibrated Machine Learning Models"]
    Detection --> SimHash["SimHash 64-bit Text Clustering"]
    Detection --> Coordination["Bipartite & Temporal Botring Extraction"]

    Detection --> GraphExport["Cytoscape.js Network Graph Generator"]
    GraphExport --> Storage
```

## 2. Core Architectural Principles
1. **Explainability First**: Every computed score is accompanied by transparent signal contributions, component breakdowns, and alternative explanations.
2. **Offline Isolation & Air-Gapped Operation**: The entire platform operates in a local `.venv` using local filesystem snapshots (`data/snapshots/`) and SQLite/PostgreSQL with zero external cloud dependencies.
3. **Data Provenance & Privacy**: Ingested datasets track SHA-256 content hashes, actor metadata, and timestamps. Personal Identifiable Information (PII) is automatically anonymized with HMAC-SHA256.
4. **Idempotence & Crash Recovery**: Ingestion and scan processing are atomic and transactional. Workers recover gracefully from crashes using SQLite/PostgreSQL state machines.
