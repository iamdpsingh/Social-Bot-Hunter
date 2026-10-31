# Infrastructure Reference (Cloud / Container Templates)

> **Note on Deployment Target:** Per ADR-0011, Social Bot Hunter is configured and verified to run **locally in a Python virtual environment (`.venv`)** with zero cloud resource dependencies.

The configurations in this directory (`infra/terraform/` and `infra/cloud-run/`) are optional reference templates for enterprise or multi-tenant deployments that choose to provision cloud infrastructure (Google Cloud Platform, Cloud Run, Cloud SQL). They are **not required** for running the platform or completing investigations.

For the active, self-contained local deployment instructions, refer to:
- [docs/deployment.md](../../docs/deployment.md)
- [scripts/run_local.sh](../../scripts/run_local.sh)
