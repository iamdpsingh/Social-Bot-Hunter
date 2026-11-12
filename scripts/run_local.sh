#!/usr/bin/env bash
# Social Bot Hunter — Multi-Service Local Runtime Runner
# Coordinates FastAPI REST API, background worker queue, and Next.js frontend

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

API_PORT=8000
DASHBOARD_PORT=3000
RUN_WORKER=true
RUN_FRONTEND=true
DO_STATUS=false
DO_STOP=false
DO_BACKUP=false
DO_PRUNE=false

# Parse CLI options
while [[ $# -gt 0 ]]; do
  case $1 in
    --status)
      DO_STATUS=true
      shift
      ;;
    --stop)
      DO_STOP=true
      shift
      ;;
    --backup)
      DO_BACKUP=true
      shift
      ;;
    --prune)
      DO_PRUNE=true
      shift
      ;;
    --no-frontend)
      RUN_FRONTEND=false
      shift
      ;;
    --no-worker)
      RUN_WORKER=false
      shift
      ;;
    --api-only)
      RUN_FRONTEND=false
      RUN_WORKER=false
      shift
      ;;
    --port)
      API_PORT="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Ensure runtime directories exist
mkdir -p data/snapshots data/models data/exports data/backups data/temp .run/logs

# Activate Python virtual environment
if [[ -d ".venv" ]]; then
  source .venv/bin/activate
elif [[ -n "${VIRTUAL_ENV:-}" ]]; then
  : # already active
else
  echo "--> Warning: No .venv detected. Running with system python3."
fi

# Handle --status
if [[ "${DO_STATUS}" == "true" ]]; then
  python3 -m sbh runtime-status
  exit 0
fi

# Handle --stop
if [[ "${DO_STOP}" == "true" ]]; then
  if [[ -f ".run/supervisor.pid" ]]; then
    PID=$(cat .run/supervisor.pid)
    echo "Stopping supervisor (PID ${PID})..."
    kill -TERM "${PID}" 2>/dev/null || true
    rm -f .run/supervisor.pid
  fi
  kill $(jobs -p) 2>/dev/null || true
  echo "All local services stopped."
  exit 0
fi

# Run preflight database migrations
echo "--> Ensuring database schema is current..."
python3 -m sbh migrate

# Handle pre-run backup/prune
if [[ "${DO_BACKUP}" == "true" ]]; then
  echo "--> Creating pre-start database backup..."
  python3 -m sbh db-backup
fi

if [[ "${DO_PRUNE}" == "true" ]]; then
  echo "--> Running retention sweep on storage directories..."
  python3 -m sbh storage-prune
fi

echo "=========================================="
echo " Starting Social Bot Hunter (Local Runtime)"
echo "=========================================="

cleanup() {
  echo ""
  echo "--> Shutting down local services..."
  kill $(jobs -p) 2>/dev/null || true
  wait 2>/dev/null || true
  rm -f .run/supervisor.pid
  echo "--> All services stopped cleanly."
}
trap cleanup SIGINT SIGTERM EXIT

# Write supervisor PID
echo "$$" > .run/supervisor.pid

# 1. Start FastAPI REST API
echo "--> Starting FastAPI REST API at http://127.0.0.1:${API_PORT} ..."
python3 -m uvicorn services.api.main:app --host 127.0.0.1 --port "${API_PORT}" --reload > .run/logs/api.log 2>&1 &

# 2. Start Local Worker if enabled
if [[ "${RUN_WORKER}" == "true" ]]; then
  echo "--> Starting local background worker pool..."
  python3 -m sbh worker-run > .run/logs/worker.log 2>&1 &
fi

# 3. Start Next.js frontend if enabled
if [[ "${RUN_FRONTEND}" == "true" && -f "apps/dashboard/package.json" ]]; then
  echo "--> Starting Next.js dashboard at http://127.0.0.1:${DASHBOARD_PORT} ..."
  (cd apps/dashboard && npm run dev) > .run/logs/dashboard.log 2>&1 &
fi

echo ""
echo "Social Bot Hunter is running locally!"
echo "API docs:   http://127.0.0.1:${API_PORT}/docs"
echo "API root:   http://127.0.0.1:${API_PORT}/api/v1"
echo "Dashboard:  http://127.0.0.1:${DASHBOARD_PORT}"
echo "Logs:       .run/logs/"
echo "Press Ctrl+C to stop all services."
echo ""

wait
