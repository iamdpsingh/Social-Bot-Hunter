"""POSIX signal management and graceful application termination."""

from __future__ import annotations

import signal
import sys
import threading
from collections.abc import Callable
from typing import Any


class SignalManager:
    """Manages SIGINT and SIGTERM traps with hook execution and second-signal escalation."""

    _instance: SignalManager | None = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._shutdown_event = threading.Event()
        self._hooks: list[Callable[[], Any]] = []
        self._signal_count = 0
        self._registered = False

    @classmethod
    def get_instance(cls) -> SignalManager:
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def register_signal_handlers(self) -> None:
        """Register signal handlers for SIGINT and SIGTERM on the main thread."""
        if self._registered:
            return
        try:
            signal.signal(signal.SIGINT, self._handle_signal)
            signal.signal(signal.SIGTERM, self._handle_signal)
            self._registered = True
        except (ValueError, AttributeError):
            # Happens if not called from main thread (e.g. in some test runners)
            pass

    def _handle_signal(self, signum: int, frame: Any) -> None:
        self._signal_count += 1
        if self._signal_count > 1:
            # Emergency exit on repeated signal
            sys.stderr.write(f"\nForced termination requested (signal {signum}). Exiting immediately.\n")
            sys.exit(128 + signum)

        sys.stderr.write(f"\nReceived signal {signum}. Initiating graceful shutdown...\n")
        self.trigger_shutdown()

    def register_shutdown_hook(self, hook: Callable[[], Any]) -> None:
        """Register a callback function to run when shutdown is triggered."""
        self._hooks.append(hook)

    def trigger_shutdown(self) -> None:
        """Trigger shutdown event and execute all registered hooks in reverse order."""
        if not self._shutdown_event.is_set():
            self._shutdown_event.set()
            for hook in reversed(self._hooks):
                try:
                    hook()
                except Exception as exc:
                    sys.stderr.write(f"Error in shutdown hook {hook}: {exc}\n")

    def is_shutting_down(self) -> bool:
        """Check if application is in process of shutting down."""
        return self._shutdown_event.is_set()

    def wait_for_shutdown(self, timeout: float | None = None) -> bool:
        """Block until shutdown is signaled or timeout elapses."""
        return self._shutdown_event.wait(timeout)

    def reset_for_testing(self) -> None:
        """Reset state for clean isolation between test runs."""
        self._shutdown_event.clear()
        self._hooks.clear()
        self._signal_count = 0
