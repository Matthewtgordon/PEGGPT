"""
Sandboxed execution environment using subprocess with resource limits
and isolated temporary directories.
"""
from __future__ import annotations

import logging
import subprocess
import tempfile
import resource
from typing import Any


class SandboxExecutor:
    """Executes commands in a restricted sandbox."""

    def __init__(self, max_cpu_time: int = 5, max_memory: int = 64 * 1024 * 1024):
        self.max_cpu_time = max_cpu_time
        self.max_memory = max_memory
        self.logger = logging.getLogger(__name__)

    def _limit_resources(self) -> None:
        resource.setrlimit(resource.RLIMIT_CPU, (self.max_cpu_time, self.max_cpu_time))
        resource.setrlimit(resource.RLIMIT_AS, (self.max_memory, self.max_memory))

    def run(self, command: str, timeout: int = 10) -> subprocess.CompletedProcess:
        """Run a shell command inside the sandbox."""
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=tmpdir,
                    preexec_fn=self._limit_resources,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=False,
                )
                return result
            except Exception as exc:  # pragma: no cover - defensive
                self.logger.error("Sandbox execution failed: %s", exc)
                raise
