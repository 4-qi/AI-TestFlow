from __future__ import annotations

from typing import Any

from ..llm_client import OpenAILlmClient
from ..schemas import DEFECT_ANALYSIS_SCHEMA, validate_required_keys


def run_analysis_agent(
    client: OpenAILlmClient,
    prompt: str,
    requirements: dict[str, Any],
    test_charters: dict[str, Any],
    execution_result: dict[str, Any],
) -> dict[str, Any]:
    data = client.generate_json(
        name="defect_analysis",
        system_prompt=prompt,
        user_prompt=(
            "请基于需求、测试任务和实时执行结果进行分类并判断缺陷。"
            f"\n\n需求:\n{requirements}\n\n测试任务:\n{test_charters}\n\n执行结果:\n{execution_result}"
        ),
        schema=DEFECT_ANALYSIS_SCHEMA,
    )
    validate_required_keys("defect_analysis", data, DEFECT_ANALYSIS_SCHEMA)
    return data
