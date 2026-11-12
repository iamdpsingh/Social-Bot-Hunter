"""Subprocess lifecycle management, logging redirection, and crash recovery."""

from __future__ import annotations

import logging
import os
import subprocess
import time
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

from sbh.runtime.sanitizer import sanitize_cmdline

logger = logging.getLogger(__name__)


class ProcessState(StrEnum):
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
            with open(log_path, "a", encoding="utf-8") as log_handle:
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
