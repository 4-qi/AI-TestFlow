from __future__ import annotations

from pathlib import Path
from typing import Any

from ...test_generator import render_generated_api_tests, render_generated_playwright_tests
from ..llm_client import OpenAILlmClient
from ..schemas import SCRIPT_PLAN_SCHEMA, validate_required_keys


def run_script_agent(
    client: OpenAILlmClient,
    prompt: str,
    test_cases: list[dict[str, Any]],
    backend_source: str,
    api_test_runtime: dict[str, str],
    api_target: Path,
    playwright_target: Path,
) -> dict[str, Any]:
    script_plan = client.generate_json(
        name="script_plan",
        system_prompt=prompt,
        user_prompt=(
            "请基于测试用例和后端源码生成通用自动化测试动作。\n\n"
            f"测试用例：\n{test_cases}\n\n"
            f"后端源码：\n{backend_source}"
        ),
        schema=SCRIPT_PLAN_SCHEMA,
    )
    validate_required_keys("script_plan", script_plan, SCRIPT_PLAN_SCHEMA)

    api_script = render_generated_api_tests(script_plan["api_tests"], api_test_runtime)
    playwright_script = render_generated_playwright_tests(script_plan["ui_tests"])
    api_target.parent.mkdir(parents=True, exist_ok=True)
    playwright_target.parent.mkdir(parents=True, exist_ok=True)
    api_target.write_text(api_script, encoding="utf-8")
    playwright_target.write_text(playwright_script, encoding="utf-8")
    return {
        "script_plan": script_plan,
        "api_script": str(api_target),
        "playwright_script": str(playwright_target),
    }
