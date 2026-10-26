# ADR-0011: GCP Serverless Deployment Architecture

**Status:** accepted

**Context.** The system must run securely and cost-effectively on Google Cloud Platform with minimal operational overhead, strong secret isolation, least-privilege IAM, and reproducible infrastructure.

**Decision.** Deploy target architecture on GCP using managed services defined via Terraform in `infra/terraform`:
1. **Compute**: Cloud Run for the FastAPI backend service and containerized workers. Cloud Run jobs for heavy scheduled batch migrations and retention sweeps.
2. **Database**: Cloud SQL for PostgreSQL 16 (private IP with VPC connector).
3. **Storage**: Google Cloud Storage buckets for raw dataset snapshots, ML models, and audit exports with retention policies.
4. **Queue & Scheduling**: Cloud Tasks for bounded concurrency scan execution; Cloud Scheduler for cron jobs.
5. **Security & Secrets**: Secret Manager for API keys and database credentials; Cloud IAM least-privilege service accounts.
6. **Observability**: Cloud Logging with structured JSON logs (`scan_id` correlation) and Cloud Monitoring alerts.

**Alternatives.**
- GKE (Kubernetes): Over-engineered for early phase; introduces cluster maintenance overhead.
- Compute Engine VMs: Lacks auto-scaling, container integration, and serverless cost advantages.

**Consequences.** Clean IaC in Terraform, zero local Docker prerequisites for dev testing, reproducible multi-environment (staging/prod) configurations.
