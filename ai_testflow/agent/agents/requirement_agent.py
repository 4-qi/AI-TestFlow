from __future__ import annotations

from typing import Any

from ..llm_client import OpenAILlmClient
from ..schemas import REQUIREMENT_BREAKDOWN_SCHEMA, validate_required_keys


def run_requirement_agent(client: OpenAILlmClient, prompt: str, prd_analysis: dict[str, Any]) -> dict[str, Any]:
    data = client.generate_json(
        name="requirement_breakdown",
        system_prompt=prompt,
        user_prompt=f"请基于 PRD 分析结果拆解可测试需求和测试点。\n\n{prd_analysis}",
        schema=REQUIREMENT_BREAKDOWN_SCHEMA,
    )
    validate_required_keys("requirement_breakdown", data, REQUIREMENT_BREAKDOWN_SCHEMA)
    return data
