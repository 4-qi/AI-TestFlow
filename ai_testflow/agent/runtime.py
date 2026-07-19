from __future__ import annotations

import os
import signal
import subprocess
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from ..config import TargetRuntimeConfig


class TargetServices:
    def __init__(self, runtime: TargetRuntimeConfig, project_root: Path, log_dir: Path):
        self._runtime = runtime
        self._project_root = project_root
        self._log_dir = log_dir
        self._processes: list[tuple[subprocess.Popen[str], object]] = []

    def __enter__(self) -> "TargetServices":
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.stop()

    def start(self) -> None:
        self._log_dir.mkdir(parents=True, exist_ok=True)
        try:
            for service in self._runtime.services:
                if _url_ready(service.ready_url):
                    continue
                log_path = self._log_dir / f"service-{_safe_name(service.name)}.log"
                log_file = log_path.open("w", encoding="utf-8")
                process = subprocess.Popen(
                    service.command,
                    cwd=self._project_root / service.cwd,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    text=True,
                    start_new_session=True,
                )
                self._processes.append((process, log_file))
                _wait_until_ready(
                    service.ready_url,
                    process,
                    self._runtime.startup_timeout_seconds,
                    log_path,
                )
        except Exception:
            self.stop()
            raise

    def stop(self) -> None:
        for process, _ in reversed(self._processes):
            if process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
        for process, log_file in reversed(self._processes):
            if process.poll() is None:
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    process.wait(timeout=5)
            log_file.close()
        self._processes.clear()


def _wait_until_ready(url: str, process: subprocess.Popen[str], timeout: float, log_path: Path) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Target service exited before becoming ready. See {log_path}")
        if _url_ready(url):
            return
        time.sleep(0.25)
    raise RuntimeError(f"Target service did not become ready at {url}. See {log_path}")


def _url_ready(url: str) -> bool:
    try:
        with urlopen(url, timeout=1) as response:
            return 200 <= response.status < 400
    except HTTPError as exc:
        return 200 <= exc.code < 400
    except (URLError, TimeoutError):
        return False


def _safe_name(value: str) -> str:
    return "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in value)
