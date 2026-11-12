"""Multi-service supervisor coordinating FastAPI, background workers, and dashboard."""

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
