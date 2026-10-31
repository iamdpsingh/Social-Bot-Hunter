#!/usr/bin/env bash
# Social Bot Hunter — Local Multi-Service Development Runner
# Starts FastAPI backend (port 8000) and Next.js frontend (port 3000)

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "=========================================="
echo " Starting Social Bot Hunter (Local Runtime)"
echo "=========================================="

# Activate virtualenv if present
if [[ -d ".venv" ]]; then
  echo "--> Activating Python virtual environment (.venv)..."
  source .venv/bin/activate
elif [[ -n "${VIRTUAL_ENV:-}" ]]; then
  echo "--> Using active virtual environment: ${VIRTUAL_ENV}"
else
  echo "--> Warning: No .venv detected. Running with system python3."
fi

# Ensure data directories exist
mkdir -p data/snapshots data/exports data/models data/backups

# Check database migrations
echo "--> Ensuring database schema is current..."
python3 -m sbh migrate

# Trap exit signals to terminate child processes gracefully
cleanup() {
  echo ""
  echo "--> Shutting down local services..."
  kill $(jobs -p) 2>/dev/null || true
  wait 2>/dev/null || true
  echo "--> All services stopped cleanly."
}
trap cleanup SIGINT SIGTERM EXIT

# Start FastAPI backend
echo "--> Starting FastAPI REST API at http://127.0.0.1:8000 ..."
python3 -m uvicorn services.api.main:app --host 127.0.0.1 --port 8000 --reload &
API_PID=$!

# Start Next.js frontend if apps/dashboard/package.json exists
if [[ -f "apps/dashboard/package.json" ]]; then
  echo "--> Starting Next.js dashboard at http://127.0.0.1:3000 ..."
  (cd apps/dashboard && npm run dev) &
  DASHBOARD_PID=$!
else
  echo "--> Dashboard package.json not found yet (scheduled for Day 4 build)."
fi

echo ""
echo "Social Bot Hunter is running locally!"
echo "API docs:  http://127.0.0.1:8000/docs"
echo "API root:  http://127.0.0.1:8000/api/v1"
echo "Press Ctrl+C to stop all services."
echo ""

wait
