from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from ..config import BrowserRuntimeConfig


class PlaywrightController:
    def __init__(self, runtime: BrowserRuntimeConfig, project_root: Path, log_dir: Path):
        self._runtime = runtime
        self._project_root = project_root
        self._log_dir = log_dir
        self._process: subprocess.Popen[str] | None = None
        self._stderr_file = None

    def __enter__(self) -> "PlaywrightController":
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def start(self) -> None:
        self._log_dir.mkdir(parents=True, exist_ok=True)
        controller_path = Path(__file__).with_name("playwright_controller.mjs")
        self._stderr_file = (self._log_dir / "playwright-controller.log").open("w", encoding="utf-8")
        self._process = subprocess.Popen(
            ["node", str(controller_path)],
            cwd=self._project_root / self._runtime.playwright_cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=self._stderr_file,
            text=True,
            bufsize=1,
        )
        self._request(
            {
                "command": "init",
                "browser": self._runtime.browser,
                "headless": self._runtime.headless,
                "base_url": self._runtime.base_url,
                "timeout_ms": self._runtime.action_timeout_ms,
            }
        )

    def new_charter(self) -> dict[str, Any]:
        return self._request({"command": "new_charter"})

    def observe(self, screenshot_path: Path | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"command": "observe"}
        if screenshot_path is not None:
            payload["screenshot_path"] = str(screenshot_path.resolve())
        return self._request(payload)["observation"]

    def act(self, action: dict[str, Any]) -> dict[str, Any]:
        return self._request({"command": "act", "action": action})

    def close(self) -> None:
        if self._process is not None:
            if self._process.poll() is None:
                try:
                    self._request({"command": "close"})
                except RuntimeError:
                    self._process.terminate()
                try:
                    self._process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self._process.kill()
                    self._process.wait(timeout=5)
            self._process = None
        if self._stderr_file is not None:
            self._stderr_file.close()
            self._stderr_file = None

    def _request(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self._process is None or self._process.stdin is None or self._process.stdout is None:
            raise RuntimeError("Playwright controller is not running")
        if self._process.poll() is not None:
            raise RuntimeError("Playwright controller exited unexpectedly")
        self._process.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n")
        self._process.stdin.flush()
        line = self._process.stdout.readline()
        if not line:
            raise RuntimeError("Playwright controller returned no response")
        response = json.loads(line)
        if not response.get("ok"):
            raise RuntimeError(str(response.get("error", "Playwright controller command failed")))
        return response


def validate_browser_action(action: dict[str, Any]) -> None:
    action_name = action.get("action")
    target_actions = {"fill", "click", "press", "select_option", "check"}
    if action_name in target_actions:
        target = action.get("target")
        if not isinstance(target, dict):
            raise ValueError(f"Browser {action_name} action requires target")
        if target.get("strategy") == "role" and not target.get("role"):
            raise ValueError("Browser role target requires role")
    if action_name == "navigate" and "path" not in action:
        raise ValueError("Browser navigate action requires path")
    if action_name == "fill" and "value" not in action:
        raise ValueError("Browser fill action requires value")
    if action_name == "press" and "key" not in action:
        raise ValueError("Browser press action requires key")
    if action_name == "select_option" and "option" not in action:
        raise ValueError("Browser select_option action requires option")
    if action_name == "scroll" and "direction" not in action:
        raise ValueError("Browser scroll action requires direction")
    if action_name == "wait" and "milliseconds" not in action:
        raise ValueError("Browser wait action requires milliseconds")
    if action_name == "finish":
        for key in ["status", "actual_result", "evidence"]:
            if key not in action:
                raise ValueError(f"Browser finish action requires {key}")
    supported = {"navigate", "fill", "click", "press", "select_option", "check", "scroll", "wait", "finish"}
    if action_name not in supported:
        raise ValueError(f"Unsupported browser action: {action_name}")
