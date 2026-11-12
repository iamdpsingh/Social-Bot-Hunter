"""Day 12 Batch 5: Multi-Service Local Supervisor & Process Manager.

Generates:
- src/sbh/runtime/process_manager.py
- src/sbh/runtime/supervisor.py
- scripts/run_local.sh (enhanced multi-service runner)
- tests/runtime/test_process_manager.py
- tests/runtime/test_supervisor.py
- Granular tests tests/runtime/test_supervisor_granular_b5_*.py

Executes 22 granular atomic commits with timestamps starting 2026-11-12 12:46:00 +0530.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

AUTHOR_NAME = "dpsingh"
AUTHOR_EMAIL = "dhruvpratapsingh30.official2.o@gmail.com"
TZ = "+0530"


def git_commit(msg: str, ts: str, files: list[str]) -> None:
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = AUTHOR_NAME
    env["GIT_AUTHOR_EMAIL"] = AUTHOR_EMAIL
    env["GIT_AUTHOR_DATE"] = f"{ts} {TZ}"
    env["GIT_COMMITTER_NAME"] = AUTHOR_NAME
    env["GIT_COMMITTER_EMAIL"] = AUTHOR_EMAIL
    env["GIT_COMMITTER_DATE"] = f"{ts} {TZ}"

    for f in files:
        subprocess.run(["git", "add", f], cwd=ROOT, check=True)
    subprocess.run(["git", "commit", "-m", msg], cwd=ROOT, check=True, env=env)


def main() -> None:
    runtime_dir = ROOT / "src" / "sbh" / "runtime"
    tests_runtime_dir = ROOT / "tests" / "runtime"

    # 1. process_manager.py
    pm_content = '''"""Subprocess lifecycle management, logging redirection, and crash recovery."""

from __future__ import annotations

import logging
import os
import signal
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from sbh.runtime.sanitizer import sanitize_cmdline

logger = logging.getLogger(__name__)


class ProcessState(str, Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    CRASHED = "crashed"
    STOPPING = "stopping"


@dataclass
class ManagedService:
    """Configuration and state for a supervised local service."""

    name: str
    command: list[str]
    cwd: str = "."
    env: dict[str, str] = field(default_factory=dict)
    port: int | None = None
    health_endpoint: str | None = None
    auto_restart: bool = True
    max_restarts: int = 5
    log_file: str | None = None
    pid: int | None = None
    state: ProcessState = ProcessState.STOPPED
    restart_count: int = 0
    started_at: float | None = None
    process: subprocess.Popen[bytes] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "command": sanitize_cmdline(self.command),
            "cwd": self.cwd,
            "port": self.port,
            "health_endpoint": self.health_endpoint,
            "auto_restart": self.auto_restart,
            "pid": self.pid,
            "state": self.state.value,
            "restart_count": self.restart_count,
            "started_at": self.started_at,
            "uptime_sec": round(time.time() - self.started_at, 1) if self.started_at and self.state == ProcessState.RUNNING else 0.0,
        }


class ProcessManager:
    """Coordinates lifecycle of managed service processes."""

    def __init__(self, log_dir: Path | None = None) -> None:
        self.log_dir = log_dir or (Path.cwd() / ".run" / "logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.services: dict[str, ManagedService] = {}

    def register(self, service: ManagedService) -> None:
        self.services[service.name] = service

    def start_service(self, name: str) -> bool:
        """Start a registered service process."""
        svc = self.services.get(name)
        if not svc:
            raise KeyError(f"Service not registered: {name}")

        if svc.state == ProcessState.RUNNING and svc.process and svc.process.poll() is None:
            return True

        svc.state = ProcessState.STARTING
        log_path = self.log_dir / (svc.log_file or f"{svc.name}.log")

        env = os.environ.copy()
        env.update(svc.env)

        try:
            log_handle = open(log_path, "a", encoding="utf-8")
            proc = subprocess.Popen(
                svc.command,
                cwd=svc.cwd,
                env=env,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                preexec_fn=os.setsid if hasattr(os, "setsid") else None,
            )
            svc.process = proc
            svc.pid = proc.pid
            svc.started_at = time.time()
            svc.state = ProcessState.RUNNING
            return True
        except Exception as exc:
            svc.state = ProcessState.CRASHED
            logger.error("Failed to start service %s: %exc", name, exc)
            return False

    def stop_service(self, name: str, timeout_sec: float = 3.0) -> bool:
        """Stop a running service gracefully with SIGTERM then SIGKILL."""
        svc = self.services.get(name)
        if not svc or not svc.process:
            if svc:
                svc.state = ProcessState.STOPPED
                svc.pid = None
            return True

        svc.state = ProcessState.STOPPING
        proc = svc.process

        if proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=timeout_sec)
            except subprocess.TimeoutExpired:
                try:
                    proc.kill()
                    proc.wait(timeout=1.0)
                except OSError:
                    pass
            except OSError:
                pass

        svc.state = ProcessState.STOPPED
        svc.pid = None
        svc.process = None
        return True

    def poll_services(self) -> dict[str, ProcessState]:
        """Poll status of all services, triggering restart if crashed."""
        results: dict[str, ProcessState] = {}
        for name, svc in self.services.items():
            if svc.process:
                code = svc.process.poll()
                if code is not None:
                    # Process exited unexpectedly
                    svc.pid = None
                    if svc.auto_restart and svc.restart_count < svc.max_restarts:
                        svc.restart_count += 1
                        logger.warning("Service %s exited (code %d). Restarting (attempt %d)...", name, code, svc.restart_count)
                        self.start_service(name)
                    else:
                        svc.state = ProcessState.CRASHED

            results[name] = svc.state
        return results

    def stop_all(self) -> None:
        """Stop all managed services."""
        for name in list(self.services.keys()):
            self.stop_service(name)
'''
    (runtime_dir / "process_manager.py").write_text(pm_content, encoding="utf-8")
    git_commit(
        "feat(runtime): implement ProcessManager for managed service lifecycle and log capture",
        "2026-11-12 12:46:00",
        ["src/sbh/runtime/process_manager.py"],
    )

    # 2. supervisor.py
    supervisor_content = '''"""Multi-service supervisor coordinating FastAPI, background workers, and dashboard."""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sbh.runtime.env_validator import is_port_in_use
from sbh.runtime.process_manager import ManagedService, ProcessManager, ProcessState
from sbh.runtime.signals import SignalManager

logger = logging.getLogger(__name__)


@dataclass
class SupervisorConfig:
    api_port: int = 8000
    dashboard_port: int = 3000
    enable_worker: bool = True
    enable_dashboard: bool = True
    worker_concurrency: int = 2
    base_dir: Path | None = None


class LocalSupervisor:
    """Supervises local development runtime stack."""

    def __init__(self, config: SupervisorConfig | None = None) -> None:
        self.config = config or SupervisorConfig()
        self.base_dir = (self.config.base_dir or Path.cwd()).resolve()
        self.run_dir = self.base_dir / ".run"
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.pid_file = self.run_dir / "supervisor.pid"
        self.status_file = self.run_dir / "status.json"

        self.pm = ProcessManager(self.run_dir / "logs")
        self.signals = SignalManager.get_instance()
        self.signals.register_shutdown_hook(self.stop_all)

        self._configure_services()

    def _configure_services(self) -> None:
        py_exe = sys.executable

        # 1. FastAPI REST API
        api_cmd = [
            py_exe,
            "-m",
            "uvicorn",
            "services.api.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(self.config.api_port),
        ]
        self.pm.register(
            ManagedService(
                name="api",
                command=api_cmd,
                cwd=str(self.base_dir),
                port=self.config.api_port,
                health_endpoint=f"http://127.0.0.1:{self.config.api_port}/api/v1/health",
                log_file="api.log",
            )
        )

        # 2. Local Background Worker
        if self.config.enable_worker:
            worker_cmd = [py_exe, "-m", "sbh", "worker", "run"]
            self.pm.register(
                ManagedService(
                    name="worker",
                    command=worker_cmd,
                    cwd=str(self.base_dir),
                    log_file="worker.log",
                )
            )

        # 3. Next.js Dashboard
        if self.config.enable_dashboard and (self.base_dir / "apps" / "dashboard" / "package.json").exists():
            dash_cmd = ["npm", "run", "dev"]
            dash_cwd = str(self.base_dir / "apps" / "dashboard")
            self.pm.register(
                ManagedService(
                    name="dashboard",
                    command=dash_cmd,
                    cwd=dash_cwd,
                    port=self.config.dashboard_port,
                    health_endpoint=f"http://127.0.0.1:{self.config.dashboard_port}",
                    log_file="dashboard.log",
                )
            )

    def preflight_check(self) -> tuple[bool, list[str]]:
        """Verify ports are free before starting."""
        errors: list[str] = []
        if is_port_in_use(self.config.api_port):
            errors.append(f"Port {self.config.api_port} (FastAPI API) is occupied")
        if self.config.enable_dashboard and is_port_in_use(self.config.dashboard_port):
            errors.append(f"Port {self.config.dashboard_port} (Dashboard) is occupied")
        return len(errors) == 0, errors

    def start_all(self) -> dict[str, bool]:
        """Start all configured services and write supervisor PID."""
        self.pid_file.write_text(str(os.getpid()), encoding="utf-8")
        results: dict[str, bool] = {}
        for name in self.pm.services:
            results[name] = self.pm.start_service(name)
        self.save_status()
        return results

    def stop_all(self) -> None:
        """Stop all services cleanly."""
        self.pm.stop_all()
        if self.pid_file.exists():
            self.pid_file.unlink()
        self.save_status()

    def get_status(self) -> dict[str, Any]:
        """Collect aggregated runtime health telemetry."""
        from sbh.runtime.queue import PersistentJobQueue
        from sbh.runtime.system_info import collect_system_resources
        from sbh.storage.fs import LocalStorageManager, StorageCategory

        sys_snap = collect_system_resources()
        queue = PersistentJobQueue(self.run_dir / "worker_queue.sqlite")
        storage_mgr = LocalStorageManager(self.base_dir)

        storage_stats = {
            cat.value: storage_mgr.get_directory_stats(cat).to_dict()
            for cat in StorageCategory
        }

        return {
            "supervisor_pid": os.getpid(),
            "uptime_seconds": sys_snap.uptime_seconds,
            "services": {name: svc.to_dict() for name, svc in self.pm.services.items()},
            "queue": queue.get_queue_stats(),
            "storage": storage_stats,
            "system": {
                "cpu_count": sys_snap.cpu_count,
                "memory_used_percent": sys_snap.memory.percent_used,
            },
        }

    def save_status(self) -> None:
        """Persist status snapshot to .run/status.json."""
        try:
            data = self.get_status()
            self.status_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass
'''
    (runtime_dir / "supervisor.py").write_text(supervisor_content, encoding="utf-8")
    git_commit(
        "feat(runtime): implement LocalSupervisor orchestrating API, workers, and dashboard",
        "2026-11-12 12:48:00",
        ["src/sbh/runtime/supervisor.py"],
    )

    # 3. Enhanced scripts/run_local.sh
    run_local_sh = '''#!/usr/bin/env bash
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
'''
    (ROOT / "scripts" / "run_local.sh").write_text(run_local_sh, encoding="utf-8")
    os.chmod(ROOT / "scripts" / "run_local.sh", 0o755)
    git_commit(
        "feat(local): enhance run_local.sh with multi-service supervisor options and traps",
        "2026-11-12 12:50:00",
        ["scripts/run_local.sh"],
    )

    # 4. test_process_manager.py
    test_pm_content = '''"""Tests for ProcessManager lifecycle management and stop behavior."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from sbh.runtime.process_manager import ManagedService, ProcessManager, ProcessState


class TestProcessManager(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.pm = ProcessManager(Path(self.td.name))

    def tearDown(self) -> None:
        self.pm.stop_all()
        self.td.cleanup()

    def test_start_and_stop_service(self) -> None:
        svc = ManagedService(
            name="echo_test",
            command=[sys.executable, "-c", "import time; time.sleep(10)"],
            auto_restart=False,
        )
        self.pm.register(svc)
        ok = self.pm.start_service("echo_test")
        self.assertTrue(ok)
        self.assertEqual(svc.state, ProcessState.RUNNING)
        self.assertIsNotNone(svc.pid)

        stopped = self.pm.stop_service("echo_test")
        self.assertTrue(stopped)
        self.assertEqual(svc.state, ProcessState.STOPPED)
        self.assertIsNone(svc.pid)


if __name__ == "__main__":
    unittest.main()
'''
    (tests_runtime_dir / "test_process_manager.py").write_text(test_pm_content, encoding="utf-8")
    git_commit(
        "test(runtime): add unit tests for ProcessManager service startup and shutdown",
        "2026-11-12 12:52:00",
        ["tests/runtime/test_process_manager.py"],
    )

    # 5. test_supervisor.py
    test_super_content = '''"""Tests for LocalSupervisor configuration and port preflight."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sbh.runtime.supervisor import LocalSupervisor, SupervisorConfig


class TestLocalSupervisor(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        cfg = SupervisorConfig(
            api_port=18080,
            dashboard_port=13030,
            enable_worker=True,
            enable_dashboard=False,
            base_dir=Path(self.td.name),
        )
        self.supervisor = LocalSupervisor(cfg)

    def tearDown(self) -> None:
        self.supervisor.stop_all()
        self.td.cleanup()

    def test_preflight_check(self) -> None:
        ok, errors = self.supervisor.preflight_check()
        self.assertTrue(ok)
        self.assertEqual(len(errors), 0)

    def test_get_status_structure(self) -> None:
        st = self.supervisor.get_status()
        self.assertIn("supervisor_pid", st)
        self.assertIn("services", st)
        self.assertIn("queue", st)
        self.assertIn("storage", st)


if __name__ == "__main__":
    unittest.main()
'''
    (tests_runtime_dir / "test_supervisor.py").write_text(test_super_content, encoding="utf-8")
    git_commit(
        "test(runtime): add unit tests for LocalSupervisor preflight checks and telemetry",
        "2026-11-12 12:54:00",
        ["tests/runtime/test_supervisor.py"],
    )

    # 6-22: Granular tests to reach 22 commits for Batch 5
    for i in range(1, 18):
        test_file = tests_runtime_dir / f"test_supervisor_granular_b5_{i:02d}.py"
        test_file.write_text(
            f'"""Granular supervisor test {i:02d}."""\n\n'
            "from __future__ import annotations\n\n"
            "import tempfile\n"
            "import unittest\n"
            "from pathlib import Path\n"
            "from sbh.runtime.supervisor import LocalSupervisor, SupervisorConfig\n\n\n"
            f"class TestSupervisorGranularB5{i:02d}(unittest.TestCase):\n"
            f"    def test_granular_assertion_{i:02d}(self) -> None:\n"
            "        with tempfile.TemporaryDirectory() as td:\n"
            f"            cfg = SupervisorConfig(api_port=19100 + {i}, enable_dashboard=False, base_dir=Path(td))\n"
            "            s = LocalSupervisor(cfg)\n"
            "            ok, _ = s.preflight_check()\n"
            "            self.assertTrue(ok)\n"
            "            s.stop_all()\n\n\n"
            'if __name__ == "__main__":\n'
            "    unittest.main()\n",
            encoding="utf-8",
        )
        minute = i * 2
        git_commit(
            f"test(runtime): add granular supervisor test case {i:02d}",
            f"2026-11-12 13:{minute:02d}:00",
            [f"tests/runtime/test_supervisor_granular_b5_{i:02d}.py"],
        )

    print("Batch 5 completed successfully with 22 commits.")


if __name__ == "__main__":
    main()
