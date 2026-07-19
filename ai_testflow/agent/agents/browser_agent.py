from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Callable

from ...browser.controller import PlaywrightController, validate_browser_action
from ...config import BrowserRuntimeConfig
from ..llm_client import OpenAILlmClient
from ..schemas import BROWSER_ACTION_SCHEMA, validate_required_keys


def run_browser_agent(
    client: OpenAILlmClient,
    prompt: str,
    charters: list[dict[str, Any]],
    runtime: BrowserRuntimeConfig,
    project_root: Path,
    output_dir: Path,
    system_context: dict[str, Any] | None = None,
    progress: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    actions: list[dict[str, Any]] = []
    observations: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    if not runtime.enabled:
        return {"status": "disabled", "actions": actions, "observations": observations, "results": results}

    screenshots_dir = output_dir / "screenshots"
    with PlaywrightController(runtime, project_root, output_dir) as controller:
        for charter in charters:
            charter_id = charter["charter_id"]
            execution_id = f"browser::{charter_id}"
            if progress:
                progress(f"Browser Agent - executing {charter_id}")
            controller.new_charter()
            latest_observation = _record_observation(
                controller.observe(_step_screenshot(runtime, screenshots_dir, charter_id, 0)),
                execution_id,
                0,
            )
            observations.append(latest_observation)
            execution_actions: list[dict[str, Any]] = []
            result: dict[str, Any] | None = None
            for step in range(1, runtime.max_steps_per_charter + 1):
                if progress:
                    progress(
                        f"Browser Agent - {charter_id} step {step}/{runtime.max_steps_per_charter}"
                    )
                action = client.generate_json(
                    name=f"browser_action_{_safe_name(charter_id)}_{step}",
                    system_prompt=prompt,
                    user_prompt=_browser_action_prompt(
                        charter,
                        latest_observation,
                        execution_actions,
                        system_context or {},
                    ),
                    schema=BROWSER_ACTION_SCHEMA,
                )
                validate_required_keys("browser_action", action, BROWSER_ACTION_SCHEMA)
                try:
                    validate_browser_action(action)
                except ValueError as exc:
                    result = _blocked_result(charter, execution_id, step, str(exc))
                    break
                action_record: dict[str, Any] = {
                    "execution_id": execution_id,
                    "charter_id": charter_id,
                    "step": step,
                    "before_observation_id": latest_observation["observation_id"],
                    "action": action,
                }
                if action["action"] == "finish":
                    action_record["duration_ms"] = 0
                    final_path = _finish_screenshot(runtime, screenshots_dir, charter_id, action["status"])
                    final_observation = _record_observation(
                        controller.observe(final_path), execution_id, step
                    )
                    observations.append(final_observation)
                    action_record["after_observation_id"] = final_observation["observation_id"]
                    actions.append(action_record)
                    execution_actions.append(action_record)
                    evidence = list(action["evidence"])
                    if final_observation.get("screenshot_path"):
                        evidence.append(final_observation["screenshot_path"])
                    result = {
                        "execution_id": execution_id,
                        "charter_id": charter_id,
                        "requirement_id": charter["requirement_id"],
                        "channel": "browser",
                        "status": action["status"],
                        "actual_result": action["actual_result"],
                        "evidence": evidence,
                        "steps_executed": step,
                    }
                    break
                started = time.monotonic()
                action_error = None
                try:
                    controller.act(action)
                except RuntimeError as exc:
                    action_error = str(exc)
                action_record["duration_ms"] = round((time.monotonic() - started) * 1000, 2)
                latest_observation = _record_observation(
                    controller.observe(_step_screenshot(runtime, screenshots_dir, charter_id, step)),
                    execution_id,
                    step,
                )
                if action_error:
                    latest_observation["action_error"] = action_error
                    action_record["error"] = action_error
                observations.append(latest_observation)
                action_record["after_observation_id"] = latest_observation["observation_id"]
                actions.append(action_record)
                execution_actions.append(action_record)
            if result is None:
                result = _blocked_result(
                    charter,
                    execution_id,
                    runtime.max_steps_per_charter,
                    "Browser Agent reached the maximum step count without finishing the charter",
                )
            results.append(result)
    return {
        "status": _aggregate_status(results),
        "observation_mode": runtime.observation_mode,
        "actions": actions,
        "observations": observations,
        "results": results,
    }


def _browser_action_prompt(
    charter: dict[str, Any],
    latest_observation: dict[str, Any],
    history: list[dict[str, Any]],
    system_context: dict[str, Any],
) -> str:
    model_observation = {key: value for key, value in latest_observation.items() if key != "screenshot_path"}
    return (
        "请根据测试任务、系统范围、最新页面结构化观察和动作历史决定下一步。每次只输出一个动作。\n\n"
        f"测试任务：\n{json.dumps(charter, ensure_ascii=False)}\n\n"
        f"系统范围：\n{json.dumps(system_context, ensure_ascii=False)}\n\n"
        f"最新观察：\n{json.dumps(model_observation, ensure_ascii=False)}\n\n"
        f"动作历史：\n{json.dumps(history, ensure_ascii=False)}"
    )


def _record_observation(observation: dict[str, Any], execution_id: str, step: int) -> dict[str, Any]:
    return {
        "observation_id": f"{execution_id}::observation::{step}",
        "execution_id": execution_id,
        "step": step,
        **observation,
    }


def _step_screenshot(
    runtime: BrowserRuntimeConfig,
    screenshots_dir: Path,
    charter_id: str,
    step: int,
) -> Path | None:
    if runtime.screenshot != "always":
        return None
    return screenshots_dir / f"{_safe_name(charter_id)}-step-{step}.png"


def _finish_screenshot(
    runtime: BrowserRuntimeConfig,
    screenshots_dir: Path,
    charter_id: str,
    status: str,
) -> Path | None:
    if runtime.screenshot == "off":
        return None
    return screenshots_dir / f"{_safe_name(charter_id)}-{status}.png"


def _blocked_result(
    charter: dict[str, Any], execution_id: str, step: int, reason: str
) -> dict[str, Any]:
    return {
        "execution_id": execution_id,
        "charter_id": charter["charter_id"],
        "requirement_id": charter["requirement_id"],
        "channel": "browser",
        "status": "blocked",
        "actual_result": reason,
        "evidence": [],
        "steps_executed": step,
    }


def _aggregate_status(results: list[dict[str, Any]]) -> str:
    statuses = {result["status"] for result in results}
    if "failed" in statuses:
        return "failed"
    if "blocked" in statuses:
        return "blocked"
    return "passed"


def _safe_name(value: str) -> str:
    return "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in value)
