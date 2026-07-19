from __future__ import annotations

import json
import time
from typing import Any, Callable

from ...config import ApiRuntimeConfig
from ..http_controller import HttpController, validate_api_action
from ..llm_client import OpenAILlmClient
from ..schemas import API_ACTION_SCHEMA, validate_required_keys


def run_api_agent(
    client: OpenAILlmClient,
    prompt: str,
    charters: list[dict[str, Any]],
    runtime: ApiRuntimeConfig,
    system_context: dict[str, Any] | None = None,
    progress: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    actions: list[dict[str, Any]] = []
    observations: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    if not runtime.enabled:
        return {"status": "disabled", "actions": actions, "observations": observations, "results": results}

    for charter in charters:
        charter_id = charter["charter_id"]
        execution_id = f"api::{charter_id}"
        if progress:
            progress(f"API Agent - executing {charter_id}")
        controller = HttpController(runtime.base_url, runtime.request_timeout_seconds)
        latest_observation: dict[str, Any] = {
            "observation_id": f"{execution_id}::observation::0",
            "execution_id": execution_id,
            "step": 0,
            "message": "No API request has been sent in this execution.",
        }
        observations.append(latest_observation)
        result: dict[str, Any] | None = None
        execution_actions: list[dict[str, Any]] = []
        for step in range(1, runtime.max_steps_per_charter + 1):
            if progress:
                progress(f"API Agent - {charter_id} step {step}/{runtime.max_steps_per_charter}")
            action = client.generate_json(
                name=f"api_action_{_safe_name(charter_id)}_{step}",
                system_prompt=prompt,
                user_prompt=_api_action_prompt(
                    charter,
                    latest_observation,
                    execution_actions,
                    system_context or {},
                ),
                schema=API_ACTION_SCHEMA,
            )
            validate_required_keys("api_action", action, API_ACTION_SCHEMA)
            try:
                validate_api_action(action)
            except ValueError as exc:
                result = _blocked_result(charter, execution_id, step, str(exc))
                break
            action_record = {
                "execution_id": execution_id,
                "charter_id": charter_id,
                "step": step,
                "action": action,
            }
            if action["action"] == "finish":
                action_record["duration_ms"] = 0
                actions.append(action_record)
                execution_actions.append(action_record)
                result = {
                    "execution_id": execution_id,
                    "charter_id": charter_id,
                    "requirement_id": charter["requirement_id"],
                    "channel": "api",
                    "status": action["status"],
                    "actual_result": action["actual_result"],
                    "evidence": action["evidence"],
                    "steps_executed": step,
                }
                break
            started = time.monotonic()
            observation = controller.request(action)
            action_record["duration_ms"] = round((time.monotonic() - started) * 1000, 2)
            actions.append(action_record)
            execution_actions.append(action_record)
            latest_observation = {
                "observation_id": f"{execution_id}::observation::{step}",
                "execution_id": execution_id,
                "step": step,
                **observation,
            }
            observations.append(latest_observation)
        if result is None:
            result = _blocked_result(
                charter,
                execution_id,
                runtime.max_steps_per_charter,
                "API Agent reached the maximum step count without finishing the charter",
            )
        results.append(result)
    return {
        "status": _aggregate_status(results),
        "actions": actions,
        "observations": observations,
        "results": results,
    }


def _api_action_prompt(
    charter: dict[str, Any],
    latest_observation: dict[str, Any],
    history: list[dict[str, Any]],
    system_context: dict[str, Any],
) -> str:
    return (
        "请根据测试任务、最新真实接口观察和动作历史决定下一步。每次只输出一个动作。\n\n"
        f"测试任务：\n{json.dumps(charter, ensure_ascii=False)}\n\n"
        f"系统接口范围：\n{json.dumps(system_context, ensure_ascii=False)}\n\n"
        f"最新观察：\n{json.dumps(latest_observation, ensure_ascii=False)}\n\n"
        f"动作历史：\n{json.dumps(history, ensure_ascii=False)}"
    )


def _blocked_result(
    charter: dict[str, Any], execution_id: str, step: int, reason: str
) -> dict[str, Any]:
    return {
        "execution_id": execution_id,
        "charter_id": charter["charter_id"],
        "requirement_id": charter["requirement_id"],
        "channel": "api",
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
