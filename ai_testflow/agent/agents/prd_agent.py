from __future__ import annotations

from typing import Any

from ..llm_client import OpenAILlmClient
from ..schemas import PRD_ANALYSIS_SCHEMA, validate_required_keys


def run_prd_agent(client: OpenAILlmClient, prompt: str, prd_text: str) -> dict[str, Any]:
    data = client.generate_json(
        name="prd_analysis",
        system_prompt=prompt,
        user_prompt=f"请分析以下 PRD，并只输出符合 schema 的 JSON。\n\n{prd_text}",
        schema=PRD_ANALYSIS_SCHEMA,
    )
    validate_required_keys("prd_analysis", data, PRD_ANALYSIS_SCHEMA)
    return data
