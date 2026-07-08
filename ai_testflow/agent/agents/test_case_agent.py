from __future__ import annotations

from typing import Any

from ..llm_client import OpenAILlmClient
from ..schemas import TEST_CASE_SCHEMA, validate_required_keys


def run_test_case_agent(client: OpenAILlmClient, prompt: str, requirement_breakdown: dict[str, Any]) -> dict[str, Any]:
    data = client.generate_json(
        name="test_case_design",
        system_prompt=prompt,
        user_prompt=f"请基于需求和测试点设计接口和页面自动化测试用例。\n\n{requirement_breakdown}",
        schema=TEST_CASE_SCHEMA,
    )
    validate_required_keys("test_case_design", data, TEST_CASE_SCHEMA)
    return data
