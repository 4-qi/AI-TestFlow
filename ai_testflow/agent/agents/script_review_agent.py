from __future__ import annotations

from typing import Any

from ..llm_client import OpenAILlmClient
from ..schemas import SCRIPT_PLAN_SCHEMA, validate_required_keys


def run_script_review_agent(
    client: OpenAILlmClient,
    prompt: str,
    script_plan: dict[str, Any],
    test_cases: list[dict[str, Any]],
    prd_text: str,
    backend_source: str,
) -> dict[str, Any]:
    reviewed_plan = client.generate_json(
        name="script_plan",
        system_prompt=prompt,
        user_prompt=(
            "请审查并修正自动化测试动作，输出修正后的完整 script_plan。\n\n"
            f"PRD：\n{prd_text}\n\n"
            f"测试用例：\n{test_cases}\n\n"
            f"后端源码：\n{backend_source}\n\n"
            f"待审查脚本计划：\n{script_plan}"
        ),
        schema=SCRIPT_PLAN_SCHEMA,
    )
    validate_required_keys("script_plan", reviewed_plan, SCRIPT_PLAN_SCHEMA)
    return reviewed_plan
